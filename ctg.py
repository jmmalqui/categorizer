import argparse
import logging
from pathlib import Path
import os
import shutil


class CustomFormatter(logging.Formatter):
    """
    https://stackoverflow.com/questions/384076/how-can-i-color-python-logging-output"""

    grey = "\x1b[36;20m"
    green = "\x1b[32;20m"

    yellow = "\x1b[33;20m"
    red = "\x1b[31;20m"
    bold_red = "\x1b[31;1m"
    reset = "\x1b[0m"
    format = "[%(name)s] - %(levelname)s - %(message)s (%(filename)s:%(lineno)d)"

    FORMATS = {
        logging.DEBUG: grey + format + reset,
        logging.INFO: green + format + reset,
        logging.WARNING: yellow + format + reset,
        logging.ERROR: red + format + reset,
        logging.CRITICAL: bold_red + format + reset,
    }

    def format(self, record):
        log_fmt = self.FORMATS.get(record.levelno)
        formatter = logging.Formatter(log_fmt)
        return formatter.format(record)


logger = logging.getLogger("CTG")
logger.setLevel(logging.DEBUG)

ch = logging.StreamHandler()
ch.setLevel(logging.DEBUG)

ch.setFormatter(CustomFormatter())

logger.addHandler(ch)

p = argparse.ArgumentParser()

p.add_argument("source")
p.add_argument("target")


args = p.parse_args()
source_dir = Path(args.source)
target_dir = Path(args.target)
if not source_dir.exists():
    logger.critical("Source dir is invalid, closing. . .")
    raise SystemExit(1)


logger.info("Source Directory read succesfully.")

if not target_dir.exists():
    logger.critical("Target dir is invalid, closing. . .")
    raise SystemExit(1)

logger.info("Target Directory read succesfully.")

dir_dict = {}
for entry in source_dir.iterdir():
    if entry.suffix != "":
        logger.debug(entry.name)
        logger.info(f"Adding {entry.suffix} extension.")

        if entry.suffix in dir_dict:
            dir_dict[entry.suffix].append(entry.name)
        else:
            dir_dict[entry.suffix] = [entry.name]
ext_num = len(dir_dict.keys())
logger.debug(f"{ext_num} extensions found.")

print("\n")
for key, value in dir_dict.items():
    logger.info(f"The following {key} directories where found:")
    if key == "":
        logger.critical("No extension files would not be packed")
        continue
    for _dir in dir_dict[key]:
        logger.debug(_dir)
    target_pack_directory = f"{key[1:]}_files"
    logger.warning(
        f"Do you want to pack these directories into this single file: {os.path.join(target_dir,target_pack_directory)}? [Y/N]"
    )
    yes_no = input()
    if yes_no.lower() in ["y", "yes"]:
        logger.warning(f"Packing into {os.path.join(target_dir,target_pack_directory)}")

        pack_path = Path(os.path.join(target_dir, target_pack_directory))
        if pack_path.exists():
            logger.info("Directory already exists, skipping directory creation.")
        else:
            logger.info("Creating File...")
            os.mkdir(pack_path)
            if pack_path.exists():
                logger.debug(f"{pack_path} created successfully.")
            else:
                logger.critical(f"{pack_path} could not be created.")
        logger.warning("Transferring files")
        for _dir in dir_dict[key]:
            dest = Path(os.path.join(pack_path, _dir))
            source = Path(os.path.join(source_dir, _dir))
            logger.info(f"Moving {dest}")
            shutil.move(source, dest)
        print("\n")
    else:
        logger.warning(f"Ignoring {os.path.join(source_dir,target_pack_directory)}")
        print("\n")
        continue
if ext_num == 0:
    logger.warning("No files to pack where found.")
logger.info("File Transfer Succeded")
