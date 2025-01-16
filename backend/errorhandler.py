import time

# HANDLE TIMEOUT ERRORS
def make_request_with_retries(func, max_retries=3, delay=2, *args, **kwargs):
    retries = 0
    while retries < max_retries:
        try:
            return func(*args, **kwargs)
        except Exception as e:
            retries += 1
            delay = delay * (2 ** retries)  # Exponential backoff
            print(f"Request failed ({e}), retrying in {delay} seconds...")
            time.sleep(delay)
    raise Exception(f"All {max_retries} retries failed.")