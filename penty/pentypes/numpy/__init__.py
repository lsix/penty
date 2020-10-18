from penty.pentypes import builtins as penbuiltins
from penty.types import Module as _Module, Cst as _Cst, Type as _Type
from penty.types import astype as _astype
import typing as _typing
import numpy
import itertools

#
##

class NDArrayMeta(type):
    cache = {}
    def __getitem__(self, args):
        if args not in NDArrayMeta.cache:
            class LocalNDArray(NDArray):
                __args__ = args
            NDArrayMeta.cache[args] = LocalNDArray
        return NDArrayMeta.cache[args]

    def __repr__(self):
        return 'NDArray[{}]'.format(', '.join(map(str, self.__args__)))



class NDArray(metaclass=NDArrayMeta):
    pass

def ndarray_getitem(base_ty, self_ty, key_ty):
    from penty.penty import Types
    dtype_ty, shape_ty= base_ty.__args__

    if _astype(key_ty) is int:
        if len(shape_ty.__args__) == 1:
            return dtype_ty
        else:
            return NDArray[dtype_ty,
                           _typing.Tuple[shape_ty.__args__[1:]]]
    if _astype(key_ty) is slice:
        return ndarray_getitem(base_ty, self_ty, _typing.Tuple[key_ty])

    if issubclass(_astype(key_ty), tuple) :
        if len(shape_ty.__args__) < len(key_ty.__args__):
            raise TypeError
        new_shape = ()
        padded_indices_dims = itertools.zip_longest(key_ty.__args__,
                                                    shape_ty.__args__,
                                                    fillvalue=slice)
        for index, dim in padded_indices_dims:
            if index is int:
                continue
            if index is slice:
                new_shape += _astype(dim),
                continue
            if issubclass(index, _Cst):
                index = index.__args__[0]
                if isinstance(index, int):
                    continue
                if isinstance(index, slice):
                    if issubclass(dim, _Cst):
                        dim_v = dim.__args__[0]
                        new_shape += _Cst[len([0] * dim_v)[index]]
                    elif index.stop is None or index.stop < 0:
                        new_shape += int,
                    else:
                        start = 0 if index.start is None else index.start
                        step = 1 if index.step is None else index.step
                        if start < 0:
                            new_shape += int,
                        else:
                            new_shape += _Cst[(index.stop - start) // step],
                    continue
                raise TypeError
            raise TypeError
        if new_shape:
            return NDArray[dtype_ty, _typing.Tuple[new_shape]]
        else:
            return dtype_ty
    raise TypeError(key_ty)

#
##

def ones_(shape_ty, dtype_ty=None):
    if dtype_ty is None:
        dtype_ty = float
    elif issubclass(dtype_ty, _Type):
        dtype_ty = dtype_ty.__args__[0]
    else:
        raise NotImplementedError
    if shape_ty is int or issubclass(shape_ty, _Cst):
        return NDArray[dtype_ty, _typing.Tuple[shape_ty]]
    if issubclass(shape_ty, _typing.Tuple):
        return NDArray[dtype_ty, shape_ty]
    raise NotImplementedError

def ndarray_instanciate(ty):
    return {
        '__getitem__': _Cst[lambda *args: ndarray_getitem(ty, *args)],
    }

#
##

def register(registry):
    if _Module['numpy'] not in registry:
        registry[NDArray] = ndarray_instanciate
        registry[_Module['numpy']] = {
            'ones': _Cst[ones_],
            'random': _Module['numpy.random'],
        }