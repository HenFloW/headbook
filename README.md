# “HeadBook” Example Project (INF226, 2023)

-   Flask docs: https://flask.palletsprojects.com/en/3.0.x/
-   Flask login docs: https://flask-login.readthedocs.io/en/latest/
-   Using "Log in with _social network_": https://python-social-auth.readthedocs.io/en/latest/configuration/flask.html

## To Use

### Set up virtual environment and install dependencies

Use the [`venv`](https://docs.python.org/3/library/venv.html) command to create a virtual environment. E.g., on Unix (see web page for how to use it on Windows and with non-Bourne-like shells):

```sh
cd 226book
python -m venv .venv  # or possibly python3
. .venv/bin/activate  # yes there's a dot at the beginning of the line
pip install -r requirements.txt
```

You can exit the virtual environment with the command `deactivate`.

### Run it

```sh
flask -A headbook:app run --reload
```

### Add .env file

**This should be in the root directory**

```sh
SECRET_KEY=\<your_secret_key\> # Replace with your own secret key and make it long

# Gitlab OAuth
GITLAB_CLIENT_ID=\<your_client_id\>
GITLAB_CLIENT_SECRET=\<your_client_secret\>
```

### Markdown awnsers for questions

#### [Awnsers for 2a)](anwsers/2a.md)

#### [Awnsers for 2b)](anwsers/2b.md)

#### [Awnsers for 2c)](anwsers/2c.md)

#### [Awnsers for 2d)](anwsers/2d.md)

#### [Awnsers for 2e)](anwsers/2e.md)

_Review of Joachim.Henriksen_headbook_

#### [Awnsers for 3a)](anwsers/3a.md)

_Improvements made in 3b_

#### [Improvements for 3b)](anwsers/3b.md)

To se the final commit for task 2 go to this commit: [Final commit for task 2](https://git.app.uib.no/inf226/23h/assignment-2/Henrik.F.Wilhelmsen_headbook/-/tree/4126b83591de45682ba9b4b3f611d68d9b50d8ff)

This can be viewed locally by checking out to `git checkout 4126b83591de45682ba9b4b3f611d68d9b50d8ff`

The current commit is the final commit for task 3.

# Copyright

-   `unknown.png` – from [OpenMoji](https://openmoji.org/about/) ([Attribution-ShareAlike 4.0 International](https://creativecommons.org/licenses/by-sa/4.0/))
-   `favicon.(png|ico)` – from [Game Icons](https://game-icons.net/1x1/skoll/knockout.html) ([CC BY 3.0](http://creativecommons.org/licenses/by/3.0/))
-   `uhtml.js` – from [µHTML](https://github.com/WebReflection/uhtml) (Copyright (c) 2020, Andrea Giammarchi, [ISC License](https://opensource.org/license/isc-license-txt/))
-   Base code by Anya

-   `gitlab svg` - from [Gitlab](https://about.gitlab.com/press/press-kit/)
