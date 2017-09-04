# coding: utf-8

# #####
# #
# # args kwargs
# #
# def testargs(*args, **kwargs):
#     print(args)
#     print(type(args))
#     print(kwargs)

# testargs(a=4,b=5)

# #########
# # 
# # simple decorator
# # 
# from functools import wraps
# # wraps的作用是更新作wrapper function，
# # 让wrapped function的特性（__docs__，__name__等)显现出来
# # 不加wraps这个装饰器会丢失这类特性。
# def decB(funcname):
#     @wraps(funcname)
#     def funcb(*args):
#         return "[{0}]".format(funcname(*args))
#     return funcb

# def decA(funcname):
#     # @wraps(funcname)
#     def funca(*args):
#         return ".{0}.".format(funcname(*args))
#     return funca

# @decB
# @decA
# def testdecA(ctx):
#     return "<{0}>".format(ctx)

# print(testdecA("a"))
# print(testdecA.__name__)

# ######
# # 
# # Decorators Takes Arguments
# # 
# def takearg(*args):
#     def takefuncname(funcname):
#         def takefuncparam(*argsss):
#             return "<<<{1}>>>{0}<<<{1}>>>".format(funcname(*argsss), *args)
#             # return "<<<{1}>>>{0}<<<{1}>>>".format(funcname(argsss), args)
#         return takefuncparam
#     return takefuncname

# @takearg("1")
# def testpassdecarg(arg1):
#     return "*{0}*".format(arg1)

# print(testpassdecarg("hehe"))
# print(testpassdecarg.__name__)
