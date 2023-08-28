# developer_salaries

Current average salaries in Moscow for 
[Github's top programming languages of 2021](https://octoverse.github.com/#top-languages-over-the-years)
in your terminal. Based on data from 
[HeadHunter](https://github.com/hhru/api/blob/master/README.md#headhunter-api)
and [SuperJob](https://api.superjob.ru/).

## How to install

### Install the required packages
Python3 should be already installed. 
Use `pip` to install dependencies:
```console
$ python3 -m pip install -r requirements.txt
```
Optionally, you can use [virtualenv](https://docs.python-guide.org/dev/virtualenvs/#lower-level-virtualenv) 
to install the packages inside a virtual environment and not on your entire system. 
In this case you will need to run the script from the virtual environment as well.

### Get an API key for SuperJob
Head over to [SuperJob API portal](https://api.superjob.ru/register),
create an account and register your app.
You can put any website in the website field, existing or not. 
No one will know.

When you see a long string with as many as _four_ periods in it,
copy it and put it into the file named '.env' 
(create the file in the project directory) like so:
```
SUPERJOB_KEY=v3.r.some-numbers.some-random-characters.more-random-characters
```

### Or don't
Honestly though, if you don't want to bother registering an app, that's fine. 
The data from SuperJob is like 1/1000 the size of the data from HeadHunter.
Just don't forget to comment out the lines in `main()` that are responsible for
fetching vacancies from SuperJob:
```python
def main():
    # load_dotenv()
    # superjob_key = os.getenv('SUPERJOB_KEY')
    # salaries_sj = get_salaries_for_top_languages_sj(superjob_key)
    # print_salaries_as_table(salaries_sj, table_title='SuperJob Moscow')

    salaries_hh = get_salaries_for_top_languages_hh()
    print_salaries_as_table(salaries_hh, table_title='HeadHunter Moscow')
```
Uncomment them later when you feel like checking if more vacancies are available from SuperJob.

## How to use:
Run the file:
```commandline
$ python3 main.py
```
and choose your destiny.
