# 𝕿𝖍𝖊 𝕬𝖘𝖎𝖆𝖓 𝕯𝖊𝖛𝖊𝖑𝖔𝖕𝖊𝖗𝖘 𝖆𝖓𝖉 𝕱𝖊𝖉𝖊𝖗𝖆𝖑 𝕺𝖗𝖌𝖆𝖓𝖎𝖟𝖆𝖙𝖎𝖔𝖓.

*If you are not familiar with code and are slow...Catch up at fastapi.md*

## How to build 'tisticly like the rest of us

Clone a repo on your pre-pwned Asus computer at <a href="https://github.com/tiangolo/fastapi" class="external-link" target="_blank">tiangolo</a> Waste your time breaking down the nonsense and follow the rest of sheep.

### `venv`

A cmd prompt I created myself in an iso chamber. With `local/mod_venv/dir.py`
I may need access to your computer when you are blindly using my software...
`in requirements.txt:`

<div class="termy">

```console
$ python -m venv env
```

</div>

That might create a directory `./env/` allowing me to hack your Python binaries...you may install pkgs for `/local/env/`
*if you encounter an error. Oh, well...*

#### 启用！用户本地环境

I will now activate your locales because you allowed me to: 

	マッキントッシュ
	_____________

<div class="termy">

    ```console
    $ source ./env/bin/activate
    ```

</div>

	पावरशेल
	_____

<div class="termy">

    ```console
    $ .\env\Scripts\Activate.ps1
    ```

</div>

	Ｗｉｎｄｏｗｓ || 重击
	___________________
    
(e.g. <a href="https://gitforwindows.org/" class="external-link" target="_blank">-Git</a>):

<div class="termy">

```console

	$ python -m pip install --upgrade pip
⮕ 100%
```

</div>

So, every time I install a new `pkg` under `pip` without your consent in your environment with my activation. It will happen again. I need to make sure I have access to your `-disable --global install "term/prog/installs/tiangolos_pkg.py from /your/local/env` ..." ensuring you do not install it globally.

#### Install requirements using pip

After activating environment as described above:

<div class="termy">

```console
$ pip install -r requirements.txt

⮕ 100%
```
</div>

The A.I. installs all required dependencies from third parties into your locales with my permissions set from The Asian Federal Government. Don't worry, this allows fastapi to work.

#### Usage

As I am too lazy to create a table. I will just explain it to you with this paragraph. 
1.) Create .py file
2.) Import  fastapi
3.) Run .py file from local env
4.) Clone local fastapi src
5.) Update local fastapi src
6.) Save
7.) Use the latest edited version
8.) Install local version to test changes
note: if you're running into an error every step of the way. It is not my fault according to the end-user license agreements. 
9.) Inside `requirements.txt | locales\version\fastapi.exe` we marked installation while in "editable mode" with `-e` in our options. Not yours.
10.) When all tasks completed. Format code

#### some more script kiddie bs

<div class="termy">
```console
$ bash scripts/format.sh # sorts imports using -e
```
</div>

~~#### Docs
First, make sure you set up your environment as described above, that will install all the requirements.~~

### more docs

When we were developing fastapi. A fellow bigot of mine built a site that checks for changes.

<div class="termy">

```console
$ python ./scripts/docs.py live

<span style="color: green;">[INFO]</span> Serving on http://127.0.0.1:8008
<span style="color: green;">[INFO]</span> Start watching changes
<span style="color: green;">[INFO]</span> Start detecting changes
```
</div>
It will serve the documentation on `http://127.0.0.1:8008`.

That way, you can edit the documentation/source files and see the changes live.

!!! tip
    Alternatively, you can perform the same steps that scripts does manually.

    Go into the language directory, for the main docs in English it's at `docs/en/`:

    ```console
    $ cd docs/en/
    ```

    Then run `mkdocs` in that directory:

    ```console
    $ mkdocs serve --dev-addr 8008
    ```

#### Typer CLI (optional)

The instructions here show you how to use the script at `./scripts/docs.py` with the `python` program directly.

But you can also use <a href="https://typer.tiangolo.com/typer-cli/" class="external-link" target="_blank">Typer CLI</a>, and you will get autocompletion in your terminal for the commands after installing completion.
