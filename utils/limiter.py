from slowapi import Limiter
from slowapi.util import get_remote_address

# 创建限流器实例，使用客户端 IP 作为标识
limiter = Limiter(key_func=get_remote_address)
