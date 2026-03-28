mkdir -p .jwt
ssh-keygen -t rsa -b 4096 -m PEM -N '' -f .jwt/jwtRS256.key
openssl rsa -in .jwt/jwtRS256.key -pubout -outform PEM -out .jwt/jwtRS256.key.pub