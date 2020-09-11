import asyncio
import asynctest
import inspect

class AsyncResync:
    """
    Re-synchronizes every async function on a given object.
    NOTE: Every method runs on a new loop
    """

    class _AsyncResyncMethod:
        def __init__(self, func):
            self.func = func
        def __call__(self, *args, **kwargs):
            coroutine = self.func(*args, **kwargs)
            loop = asyncio.new_event_loop()
            retval = loop.run_until_complete(coroutine)
            loop.close()
            return retval

    def __getattr__(self, attr):
        retval = super().__getattribute__(attr)
        if inspect.iscoroutinefunction(retval):
            return self._AsyncResyncMethod(retval)
        return retval
    __getattribute__ = __getattr__


class ResyncProxy:
    """
    Proxies the underlying class, replacing coroutine methods
    with an auto-executing one
    """
    def __init__(self, cls):
        self.cls = cls

    def __call__(self, *args, **kwargs):
        class DynamicResync(AsyncResync, self.cls):
            """
            Forces a mixin of the underlying class and the AsyncResync
            class
            """
            pass
        return DynamicResync(*args, **kwargs)

    def __getattr__(self, key):
        if key == 'cls':
            return super().__getattribute__(key)
        return getattr(self.cls, key)

class AsyncMagicMock:
    """
    Simple mock that returns a CoroutineMock instance for every
    attribute. Useful for mocking async libraries
    """
    def __init__(self):
        self.__attr_cache = {}

    def __getattr__(self, key):
        attr_cache = super().__getattribute__('_AsyncMagicMock__attr_cache')
        if key == '_AsyncMagicMock__attr_cache': return attr_cache
        if key not in attr_cache:
            attr_cache[key] = asynctest.CoroutineMock()
        return attr_cache[key]

    def __setattr__(self, key, val):
        if key == '_AsyncMagicMock__attr_cache':
            return super().__setattr__(key, val)
        attr_cache = super().__getattribute__('_AsyncMagicMock__attr_cache')
        attr_cache[key] = val

    def __hasattr__(self, key):
        attr_cache = super().__getattribute__('_AsyncMagicMock__attr_cache')
        return attr_cache.has_key(key)

if __name__ == '__main__':
    class TestClass:
        async def meh(self):
            return self.heh()
        def heh(self):
            return 3
    factory = ResyncProxy(TestClass)
    obj = factory()
    print(obj.meh())
