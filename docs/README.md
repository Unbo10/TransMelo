# TransMelo

## How to run modules

If you want to run `some/folder/file.py` and the file contains some import statements, you should do the following:

1. Go to the root directory of the project (e.g. `TransMelo/` if you named the directory as the repo)
2. Run `python -m some.folder.file`

> Note: Exporting the PYTHONPATH is not recommended.


## Explanation

Please refer to [the project overview](/docs/project_overview.md).


## To Do:
To - Do: 

    - [] Define the state representation (of the environment).
    - [] Define the action space.
    - [] Define the reward function.
    - [] Define the transit function (to update the state in an episode).
    - [] Update data_array to include the route k23 too