import asyncio
from functools import wraps
from tqdm import tqdm
import itertools


def chunkify(list, n):
    """Breaks a list into n chunks. Last chunk may not be equal in size to other chunks"""
    l = list
    return [l[i:i + n] for i in range(0, len(l), n)]


async def exec_async_fxn(fxn, args, extra_args=list(), chunk_size=1, desc='', progress_bar=True):
    """Executes an asynchronous function"""
    # run asynchronously
    loop = asyncio.get_event_loop()
    futures = [
        loop.run_in_executor(None, fxn, arg, *extra_args)
        for arg in args
    ]

    # collect results
    results = []

    iterator = asyncio.as_completed(futures)
    if progress_bar:
        iterator = tqdm(iterator, desc=desc, total=len(futures), unit_scale=chunk_size)

    for f in iterator:
        results.append(await f)
    return results


def asyncfunc(fxn, arg_chunks, args=list(), chunk_size=1, progress_bar=True, desc=None):
    """
    Runs a function asynchronously.

    :param fxn: function to run asynchronously
    :type fxn: function or lambda
    :param arg_chunks: arguments to apply to the function; suggested to divide list into chunks
    :type arg_chunks: list
    :return: result
    :rtype: list
    """
    # finish loop
    loop = asyncio.get_event_loop()
    if desc is None:
        desc = desc
    results = loop.run_until_complete(exec_async_fxn(fxn, arg_chunks, extra_args=args, desc=desc, progress_bar=progress_bar, chunk_size=chunk_size))
#     loop.close()
    return results


def make_async(chunk_size, progress_bar=True):
    def dec(fxn):
        @wraps(fxn)
        def wrapper(data, *args):
            chunks = chunkify(data, chunk_size)

            desc = "Running \"{}\" [size: {}, num: {}]: ".format(fxn.__name__, chunk_size, len(chunks))
            results = asyncfunc(fxn, chunks, args=args, progress_bar=progress_bar, desc=desc)
            return list(itertools.chain(*results))
        return wrapper
    return dec