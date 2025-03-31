#!/usr/bin/env python3

import connexion

from awm import encoder


def create_app():
    app = connexion.App(__name__, specification_dir='./swagger/')
    app.app.json_encoder = encoder.JSONEncoder
    app.add_api('swagger.yaml', arguments={'title': 'EOSC Application Workflow Management API'}, pythonic_params=True)
    return app


def main():
    create_app().run(port=8080)


if __name__ == '__main__':
    main()
