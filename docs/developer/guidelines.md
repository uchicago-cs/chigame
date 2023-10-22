# Developer Guidelines

## Style 

Your code must follow the [Python Style Guide](https://uchicago-cs.github.io/student-resource-guide/style-guide/python.html) 
in the [UChicago CS Student Resource Guide](https://uchicago-cs.github.io/student-resource-guide/) 

## Pre-Commit Hooks

When setting up a [local development environment](local.md), you must make sure to
install the pre-commit hooks as instructed in that page. This will run a series of
code quality checks before committing any code, and will ensure your code is
following proper style.

Often, the pre-commit hooks will automatically fix any style issues in your code,
but you must run `git add` again to add the updated files, and `git commit` to
re-run the checks.

Bear in mind that, until all the pre-commit checks pass, your commit will not
actually be created. Additionally, the first time you make a commit, you will see
several messages starting with `[INFO] Installing environment for`. This is normal,
and will only happen the first time you make a commit.

## Git branches

In general, we will be following Vincent Driessen's 
[git flow](https://nvie.com/posts/a-successful-git-branching-model/) 
model of branching. Please take a few minutes to read that article in full.

There are a few modifications we will be making to Vincent's model:

* The `main` and `dev` branches are protected in our repository. The only
  way to merge to them is via a pull request.
* Any new code must be contributed by creating a feature branch from `dev` and
  submitting a pull request from that branch into `dev`.
* Feature branches should target incremental improvements to ChiGame with
  a single pull request at the end. They are not intended to be long-lived
  branches that are merged into `dev` multiple times.
* Feature branches should follow the naming scheme `COMPONENT/DESCRIPTION`.
  For example, if someone from the Tournament team is working on adding
  a list of tournaments, the branch for
  that code might be `tournaments/list-view`. 
* Only the senior developers can create a release branch to merge code
  from `dev` into `main`.  
* You are allowed (and encouraged) to merge changes from `dev` into a
  feature branch you are working on (to pull in any new code you may need,
  and to resolve integration issues before submitting a pull request). 
  This does not require a pull request and can be done with `git merge`.  
* Never merge a feature branch into another feature branch. If another
  team is working on a feature you need, you must wait until they merge
  it into `dev` (then, you can just merge those changes into your feature
  branch).


