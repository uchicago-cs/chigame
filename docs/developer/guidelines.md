# Developer Guidelines

## Style 

ChiGame is a large codebase, and it is important that all code
is written in a consistent style. This is enforced via a series of
automated style checks, which will detect (and often automatically fix)
any style issues in the ChiGame codebase.

These checks include the following:

* [Black](https://black.readthedocs.io/en/stable/) - a code formatter that
  automatically formats your code to follow the [PEP 8](https://peps.python.org/pep-0008/)
  style guide.
* [Flake8](https://flake8.pycqa.org/en/latest/) - a linter that checks
  for common style issues in Python code.
* [isort](https://pycqa.github.io/isort/) - a tool that automatically sorts
  your imports in a consistent order.
* [djlint](https://djlint.readthedocs.io/en/latest/) - a linter that checks
  for common style issues in Django templates.
* Miscellaneous checks for trailing whitespace, missing newlines, etc.

These checks are enforced via GitHub Actions any time you push code to the
repository, and pull requests will not be approved if they don't pass
these checks.

To ensure your code already passes these checks, we suggest you get into
the habit of running the `black` command to automatically reformat your code. For example:

```raw
$ black src/chigame/games/views.py 
reformatted src/chigame/games/views.py

All done! ✨ 🍰 ✨
1 file reformatted.
```

You can also enable automatic formatting on most code editors, so you don't
have to run `black` manually. For VS Code, see [Fornatting Python in VS Code](https://code.visualstudio.com/docs/python/formatting).

Note: While `black` is only one of the tools that will be run by our automated checks,
it will typically catch most style issues, and will fix them automatically
for you.

### Pre-Commit Hooks

We also provide pre-commit hooks that will perform all these checks
before you can create a commit. This ensures that any code you commit
will pass the CI checks when the code is pushed to the repository.

The [local development environment](local.md) describes how to set up
these pre-commit hooks. Once you do, creating a commit will trigger
a series of checks that will run automatically. 

If you would like to run all the checks before creating a commit, you can
run the following:

```bash
pre-commit run --all-files
```

Often, these pre-commit hooks will automatically fix any style issues in your code,
but you must run `git add` again to add the updated files, and `git commit` to
re-run the checks. Bear in mind that, until all the pre-commit checks pass, your commit will not
actually be created. 

Note: The first time you make a commit, you will see
several messages starting with `[INFO] Installing environment for`. This is normal,
and will only happen the first time you make a commit.

## Commit Messages

Commit messages must follow the [Conventional Commits](https://www.conventionalcommits.org/)
format, with the following modifications:

- Instead of starting the commit message with `<type>[optional scope]` (e.g., `feat:`, `fix(api)`, etc.),
  you should start with the name of the component you are working on in square brackets (e.g., `[api]`, `[games]`, etc.)
- If the commit represents a work-in-progress, you can use the `WIP` prefix (e.g., `[api] WIP: add new tournaments endpoint`).
- Commit message titles must not exceed 50 characters. The lines of the body of the commit message, if any,
  must not exceed 72 characters (see the [Git 50/72 rule](https://www.midori-global.com/blog/2018/04/02/git-50-72-rule))
- If the commit relates to an issue or PR, you must include the issue/PR number
  in the commit message body, using the format `#<issue number>` (e.g., `#42`). This
  ensures the commit is linked to the issue/PR in GitHub.

We also recommend reading [How to Write a Git Commit Message](https://chris.beams.io/posts/git-commit/) for more
details on how to compose the title and body of the commit message.

Here are a few examples of valid commit messages:

```
[games] Add missing header to game listing page
```

```
[api] Fix pagination bug in game listing endpoint

Fixes: #42
```

```
[frontend] WIP: Update styles for game listing page

The new styles for the game listing page are mostly
done, but there are still a few issues with the layout
of the game cards for games with long descriptions.

WIP: #15
```

```
[users] Improve error messages on failed login attempts

Replaced previous "Invalid credentials" message with
more descriptive messages that distinguish the 
following cases:

- Invalid username
- Invalid password
- Account locked

Closes: #37
```

## Git branches

In general, we will be following the [GitHub Flow](https://docs.github.com/en/get-started/using-github/github-flow)
branching model, with the following constraints:

* The `main` and `dev` branches are protected in our repository. The only
  way to merge to them is via a pull request.
* Any new code must be contributed by creating a branch from `dev` and
  submitting a pull request from that branch into `dev`.
* Branches should target incremental improvements to ChiGame with
  a single pull request at the end. They are not intended to be long-lived
  branches that are merged into `dev` multiple times.
* Branches should follow the naming convention `COMPONENT/DESCRIPTION`.
  For example, if someone from the Tournament team is working on adding
  a list of tournaments, the branch for that code might be `tournaments/list-view`. 
* Only the senior developers can merge from `dev` into `main`.  
* You are allowed (and encouraged) to merge changes from `dev` into a
  branch you are working on (to pull in any new code you may need,
  and to resolve integration issues before submitting a pull request). 
  This does not require a pull request and can be done with `git merge`.  
* Never merge a branch into another branch. If another
  team is working on a feature you need, you must wait until they merge
  it into `dev` (then, you can just merge those changes into your branch).

Some of the above is inspired by Vincent Driessen's [git flow](https://nvie.com/posts/a-successful-git-branching-model/) 
model of branching.

