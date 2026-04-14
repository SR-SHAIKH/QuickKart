from decouple import config
print("CASHFREE_APP_ID:", repr(config("CASHFREE_APP_ID", default="")))
print("CASHFREE_SECRET_KEY:", repr(config("CASHFREE_SECRET_KEY", default="")))
print("CASHFREE_ENV:", repr(config("CASHFREE_ENV", default="TEST")))