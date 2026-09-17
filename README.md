# JWKS

# JWKS Server

Emilio Arellano  
**Course:** CSCE 3550  
**Project:** RESTful JWKS Server

## Overview

This project implements a RESTful JWKS (JSON Web Key Set) server using Python and Flask. The server generates RSA key pairs, assigns unique Key IDs (`kid`), tracks key expiration, serves public keys in JWKS format, and issues signed JWTs.

The project supports both valid and expired JWT issuance for testing purposes.

---

## Features

- RSA key pair generation
- Unique `kid` values for each key
- Key expiration support
- JWKS endpoint
- JWT authentication endpoint
- Expired JWT support
- RS256 token signing
- Pytest test suite
- 98% test coverage

---

## Requirements

Install dependencies:

```bash
pip install flask pyjwt cryptography pytest pytest-cov