# -*- coding: utf-8 -*-
import os
import re
import sys
import shutil
import pathlib
import logging
import argparse
import numpy as np
import pandas as pd
import cv2
from tqdm import tqdm
from selenium.common.exceptions import WebDriverException

from core.image_downloader import (
    get_arg_parser,
    process_proxy
)
from core.downloader import download_images
from core.crawler import crawl_image_urls


DEFAULT_STARTING_NUMBER = 1
RELEVANCE_REGEX = re.compile('[0-9]+')


def eprint(*args, **kwargs):
    print(*args, file=sys.stderr, **kwargs)


if __name__ == '__main__':
    # Argument parser
    parser = get_arg_parser(keywords_required=False)
    parser.add_argument(
        '--keywords', 
        '-k',
        metavar='STRING', 
        default=None,
        type=str, 
        help='Keywords separated by comma (,).'
    )
    parser.add_argument(
        '--format-filter', 
        metavar='STRING', 
        required=False,
        default='jpg,jpeg,png,webp',
        help='case insensitive formats separated by comma (,)')
    parser.add_argument(
        '--file', 
        '-f',
        metavar='DIR', 
        default=None, 
        type=str, 
        help='Path to the input file.'
    )
    parser.add_argument(
        '--input-type', 
        type=str, 
        default=None,
        help='File type (default: inferred).', 
        choices=['txt', 'csv', 'tsv', 'excel', 'stdin', 'cmd'])
    parser.add_argument(
        '--begin', 
        metavar='INT', 
        required=False, 
        default=None,
        type=int, 
        help='The beginning row number (excluding the header row).')    
    parser.add_argument(
        '--end', 
        metavar='INT', 
        required=False, 
        default=None,
        type=int, 
        help='The last row number (default to the last row).')
    parser.add_argument(
        '--column-index', 
        metavar='INT', 
        required=False, 
        default=None,
        type=int, 
        help='The index of the desired column.')
    parser.add_argument(
        '--column-name', 
        metavar='STRING', 
        required=False, 
        default=None,
        type=str, 
        help='The name of the desired column.')
    parser.add_argument(
        '--exclude-header', 
        action='store_true', 
        required=False, 
        default=False,
        help='Exclude the header from the input file.')
    parser.add_argument(
        '--max-attempts', 
        metavar='INT', 
        required=False, 
        default=5,
        type=int, 
        help='Maximum number of attempts allowed to get the required number of images.')
    parser.add_argument(
        '--required-number', 
        metavar='INT',
        default=None,
        type=int,
        help='Required number of images to download for the keywords (default: any).')
    parser.add_argument(
        '--file-prefix', 
        metavar='STRING', 
        required=False, 
        default=None,
        type=str, 
        help='File prefix (default: current keyword).')
    parser.add_argument(
        '--min-dim', 
        metavar='STRING', 
        required=False,
        default='0,0',
        help='Minimum dimension of the image (default: none)')
    parser.add_argument(
        '--sort', 
        metavar='STRING', 
        required=False,
        default='rank,asc',
        help='The criteria for sorting (default: rank,asc). Example: resolution,desc')
    parser.add_argument(
        '--echo-only', 
        action='store_true', 
        required=False, 
        help='Only output the keywords in comma-separated format.')
    parser.add_argument(
        '--remove-extra', 
        action='store_true', 
        required=False, 
        help='Only keep the minimum number of images.')
    parser.add_argument(
        '--starting-number', 
        metavar='INT',
        default=DEFAULT_STARTING_NUMBER,
        type=int,
        help='Your preference of the starting number (default: 1).')
    parser.add_argument(
        '--verbose', 
        action='store_true', 
        required=False, 
        help='Show debug information.')
    parser.add_argument(
        '--include-index', 
        action='store_true', 
        required=False, 
        help='Include the index in the folder name.')
    parser.add_argument(
        'stdin', 
        nargs='?', 
        type=argparse.FileType('r'), 
        default=sys.stdin)
    args = parser.parse_args()

    # Set the desired args.proxy_type and args.proxy
    process_proxy(args)
    # print(args)
    
    # Handle allowed file formats
    args.format_filter = args.format_filter.split(',')
    # jpg is an alias for jpeg
    if 'jpg' in args.format_filter and 'jpeg' not in args.format_filter:
        args.format_filter.append('jpeg')

    # Handle input for minimum image dimensions
    args.min_dim = [int(x) for x in args.min_dim.split(',')]
    if len(args.min_dim) != 2:
        eprint('Error: incorrect input for dimension')
        exit()

    # Handle sorting
    args.sort = args.sort.split(',')
    if len(args.min_dim) != 2:
        eprint('Error: incorrect input for sorting')
        exit()
    if args.sort[0] not in ['rank', 'resolution']:
        eprint(f'Error: unknown sorting method {args.sort[0]}')
        exit()

    # Configure the logger
    logging.basicConfig(filename='error.log', level=logging.ERROR,
                        format='[%(asctime)s] %(message)s', 
                        datefmt='%Y/%m/%d %I:%M:%S %p')

    if args.input_type is None:
        # Determine the input type
        if args.keywords is not None:
            # Provided the keywords as -k or --keywords
            args.input_type = 'cmd'
        elif not sys.stdin.isatty():
            # Provided the keywords via stdin
            args.input_type = 'stdin'
        else:
            # Determine the file type
            if args.file is None or not os.path.isfile(args.file):
                print(f'Error: path {args.file} is not a file.')
                exit()

            file_type = args.file.split('.')[-1].lower()
            if file_type in ['xlsx', 'xls']:
                args.input_type = 'excel'
            elif file_type in ['csv', 'tsv', 'txt']:
                args.input_type = file_type
            else:
                # By default, read it as a text file
                args.input_type = 'txt'

    if args.input_type == 'cmd':
        keywords = args.keywords.split(',')
    elif args.input_type == 'stdin':
        keywords = args.stdin.read().split(',')
    elif args.input_type in ['excel', 'csv', 'tsv']:
        if args.column_name is None and args.column_index is None:
            eprint('Error: neither column name nor column index is specified')
            exit()
        
        if args.input_type == 'excel':
            df = pd.read_excel(args.file, header=None if args.exclude_header else [0])
        elif args.input_type == 'csv':
            df = pd.read_csv(args.file, header=None if args.exclude_header else [0])
        elif args.input_type == 'tsv':
            df = pd.read_csv(args.file, sep='\t', header=None if args.exclude_header else [0])
        
        if args.column_index:
            # If column index is specified, use column index
            keywords = list(df.iloc[args.column_index-1])
        else:
            # Otherwise, use column name
            keywords = list(df[args.column_name])
    else:
        # Read it as text file
        with open(args.file, 'r') as f:
            keywords = list(f.read())

    # Trim the list of keywords according to user input
    # By default, use the entire length
    if args.begin is None:
        args.begin = args.starting_number
    elif args.begin < args.starting_number:
        eprint(f'Error: the starting position is less than {args.starting_number}')
        exit()
    if args.end is None:
        args.end = len(keywords)-1+args.starting_number
    num_digits = len(str(len(keywords)))
    keywords = keywords[args.begin-args.starting_number:args.end+1-args.starting_number]

    # Only echo the list
    if args.echo_only:
        print(','.join(keywords))
        exit()

    # Crawl and download
    progbar = tqdm(keywords, ncols=75, unit='keyword')
    for index, keyword in enumerate(progbar):
        progbar.set_description(keyword)
        vidx = index + args.begin

        if args.include_index:
            dst_dir = os.path.join(args.output, f'{str(vidx).zfill(num_digits)}_{keyword}')
        else:
            dst_dir = os.path.join(args.output, keyword)

        for attempt in range(args.max_attempts):
            # When there are more attempts available, remove the downloaded images
            if os.path.exists(dst_dir):
                shutil.rmtree(dst_dir)
            else:
                os.mkdir(dst_dir)

            try:
                crawled_urls = crawl_image_urls(keywords=keyword,
                                                engine=args.engine, max_number=args.max_number,
                                                face_only=args.face_only, safe_mode=args.safe_mode,
                                                proxy_type=args.proxy_type, proxy=args.proxy,
                                                browser=args.driver, image_type=args.type, 
                                                color=args.color, quiet=not args.verbose)
                images_len = download_images(image_urls=crawled_urls, dst_dir=dst_dir,
                                             concurrency=args.num_threads, timeout=args.timeout,
                                             proxy_type=args.proxy_type, proxy=args.proxy,
                                             file_prefix=None, format_filter=args.format_filter,
                                             min_dim=args.min_dim)
            except WebDriverException as e:
                logging.error(str(e).strip())
                # Handle more errors
                continue 

            if args.required_number is not None:
                # User specified the number of images required
                if images_len >= args.required_number:
                    # Skip subsequent attempts
                    break
                elif attempt == args.max_attempts - 1:
                    # Reaching the last attempt
                    logging.error(f'Only downloaded {images_len} images. But {args.required_number} ' + 
                                  f'images are required for keyword: {keyword} ({vidx}).')

        # Sorting (optional) and renaming to prefix
        # Sorting options: resolution, rank
        img_files = os.listdir(dst_dir)
        sort_criteria = []
        if args.sort[0] == 'resolution':
            for img in img_files:
                with open(os.path.join(dst_dir, img), 'rb') as img:
                    im = np.asarray(bytearray(img.read()), dtype="uint8")
                    im = cv2.imdecode(im, cv2.IMREAD_COLOR)
                    height, width = im.shape[:2]
                    sort_criteria.append(height*width)
        elif args.sort[0] == 'rank':
            sort_criteria = [int(re.search(RELEVANCE_REGEX, fn).group(0)) for fn in img_files]
        
        # Sort the files in ascending (asc) order
        sorted_files = [fn for _, fn in sorted(zip(sort_criteria, img_files))]
        # Reverse the order if descending (desc) is specified
        if args.sort[1] == 'desc':
            sorted_files = sorted_files[::-1]

        # Remove extra images
        if args.remove_extra:
            # When specified to reduce the number of images needed using --remove-extra
            if len(sorted_files) > args.required_number:
                for fn in sorted_files[args.required_number:]:
                    os.remove(os.path.join(dst_dir, fn))
            # Also remove from the list
            sorted_files = sorted_files[:args.required_number]

        # Rename the files
        curr_file_prefix = args.file_prefix
        folder_num_digits = len(str(len(sorted_files)))
        if curr_file_prefix is None:
            # If no prefix is specified, the keyword will be used as the prefix
            curr_file_prefix = keyword
        for fi, old_fn in enumerate(sorted_files):
            old_fp = os.path.join(dst_dir, old_fn)
            # NOTE: Files like example.tar.gz may have problems, but that's not an image
            file_suffix = pathlib.Path(old_fp).suffix
            # The new filenames will be Prefix01, Prefix02, ...
            new_fp = os.path.join(dst_dir, f'{curr_file_prefix}{str(fi+1).zfill(folder_num_digits)}')
            if len(file_suffix) > 0:
                new_fp = f'{new_fp}{file_suffix}'
            shutil.move(old_fp, new_fp)
    
    print("Done.")
