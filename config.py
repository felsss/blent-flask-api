import bcrypt

PREFIX = "/api"
ADMIN_PASSWORD = "admin"
SALT = bcrypt.gensalt()
# TODO/FIXME: get from env
JWT_SECRET = "d3fb12750c2eff92120742e1b334479e"
