import pathlib

import invoke.context
import invoke.tasks


@invoke.tasks.task
def create_jwt_key_pair(
    context: invoke.context.Context,
    jwt_key_dir: str = ".jwt",
    public_key_file: str = "jwtRS256.key.pub",
    private_key_file: str = "jwtRS256.key",
):
    """Create JWT key pair"""
    context.run(f"mkdir -p {jwt_key_dir}")
    private_key_path = pathlib.Path(jwt_key_dir) / private_key_file
    public_key_path = pathlib.Path(jwt_key_dir) / public_key_file
    if private_key_path.exists() or public_key_path.exists():
        print(
            f"Key(s) already exist at {private_key_path} and/or {public_key_path}. Skipping creation."
        )
        return

    with context.cd(jwt_key_dir):
        # Generate RSA private key without passphrase, quietly (non-interactive)
        context.run(f"ssh-keygen -t rsa -b 4096 -m PEM -N '' -q -f {private_key_file}")
        context.run(
            f"openssl rsa -in {private_key_file} -pubout -outform PEM -out {public_key_file}"
        )
        # Restrict private key permissions
        context.run(f"chmod 600 {private_key_file}")
