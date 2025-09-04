# Python Generators Project

This project demonstrates advanced usage of Python generators for efficient data processing with large datasets.

## Project Structure

- `seed.py`: Database setup and seeding script
- `0-stream_users.py`: Generator for streaming users one by one
- `1-batch_processing.py`: Batch processing with generators
- `2-lazy_paginate.py`: Lazy pagination implementation
- `4-stream_ages.py`: Memory-efficient aggregation

## Setup

1. Install MySQL and ensure it's running
2. Update database credentials in the scripts
3. Run `seed.py` to create database and populate with data
4. Execute the individual generator scripts

## Requirements

- Python 3.x
- mysql-connector-python
- MySQL database