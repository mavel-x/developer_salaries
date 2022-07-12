import requests
from statistics import mean
from collections import defaultdict
from dotenv import load_dotenv
import os
from terminaltables import AsciiTable
from itertools import count

top_10_languages_2021 = (
        'JavaScript',
        'Python',
        'Java',
        'TypeScript',
        'C#',
        'PHP',
        'C++',
        'C',
        'Ruby'
    )


def get_hh_vacancies(language, additional_params=None, area='Москва'):
    url = 'https://api.hh.ru/vacancies'

    # The API accepts only number IDs for areas;
    # find more at https://api.hh.ru/areas/
    areas = {
        'Москва': 1,
        'Санкт-Петербург': 2
    }
    params = {
        'text': f'программист {language}',
        'area': areas[area],
        'period': 30,
        'per_page': 100,
    }
    if additional_params:
        params.update(additional_params)
    response = requests.get(url, params=params)
    response.raise_for_status()
    return response.json()


def get_average_salary_for_language_hh(language):
    salaries = []
    vacancies_processed = 0
    vacancies_found = 0
    for page in range(20):  # Max allowed number with 100 items per page before HH stops returning data
        vacancies = get_hh_vacancies(language, additional_params={'page': page})
        if page == 0:
            vacancies_found = vacancies['found']
        for vacancy in vacancies['items']:
            predicted_salary = predict_rub_salary_hh(vacancy)
            if predicted_salary:
                salaries.append(predicted_salary)
        vacancies_processed += len(vacancies['items'])
        if page >= vacancies['pages']:
            break
    if salaries:
        average_salary = int(mean([salary for salary in salaries]))
    else:
        average_salary = 'Нет данных'
    return {
            'vacancies_found': vacancies_found,
            'vacancies_processed': vacancies_processed,
            'average_salary': average_salary,
        }


def get_sj_vacancies(api_key, language, additional_params=None):
    url = 'https://api.superjob.ru/2.0/vacancies/'
    headers = {
        'X-Api-App-Id': api_key
    }

    # The query has to be pretty specific, otherwise SJ returns very unrelated vacancies
    params = {
        'town': 'Москва',
        'catalogues': 48,  # category "Разработка, программирование"
        'keywords[0]': 'программист',
        'keywords[1][srws]': 1,  # search only in vacancy title
        'keywords[1][skwc]': 'and',
        'keywords[1][keys]': language,
        'count': 100,
    }
    if additional_params:
        params.update(additional_params)
    response = requests.get(
        url,
        headers=headers,
        params=params
    )
    response.raise_for_status()
    return response.json()


def get_average_salary_for_language_sj(api_key, language):
    salaries = []
    vacancies_processed = 0
    vacancies_found = 0
    for page in count(0):
        vacancies = get_sj_vacancies(api_key, language, additional_params={'page': page})
        if page == 0:
            vacancies_found = vacancies['total']
        for vacancy in vacancies['objects']:
            predicted_salary = predict_rub_salary_sj(vacancy)
            if predicted_salary:
                salaries.append(predicted_salary)
        vacancies_processed += len(vacancies['objects'])
        if not vacancies['more']:
            break
    if salaries:
        average_salary = int(mean([salary for salary in salaries]))
    else:
        average_salary = 'Нет данных'
    return {
        'vacancies_found': vacancies_found,
        'vacancies_processed': vacancies_processed,
        'average_salary': average_salary,
    }


def predict_salary(salary_from, salary_to):
    if not salary_to and not salary_from:
        return None
    if salary_from and salary_to:
        return (salary_from + salary_to) / 2
    if salary_from and not salary_to:
        return salary_from * 1.2
    if salary_to and not salary_from:
        return salary_to * 0.8


def predict_rub_salary_hh(vacancy):
    if not vacancy['salary']:
        return None
    if vacancy['salary']['currency'] != 'RUR':
        return None
    return predict_salary(
        vacancy['salary']['from'],
        vacancy['salary']['to']
    )


def predict_rub_salary_sj(vacancy):
    if vacancy['currency'] != 'rub':
        return None
    return predict_salary(
        vacancy['payment_from'],
        vacancy['payment_to']
    )


def get_salaries_for_top_languages_hh():
    salaries_by_language = defaultdict(dict)
    for language in top_10_languages_2021:
        salaries_by_language[language] = get_average_salary_for_language_hh(language)
    return salaries_by_language


def get_salaries_for_top_languages_sj(api_key):
    salaries_by_language = defaultdict(dict)
    for language in top_10_languages_2021:
        salaries_by_language[language] = get_average_salary_for_language_sj(api_key, language)
    return salaries_by_language


def print_salaries_as_table(salaries, table_title=None):
    rows = [
        ['Язык', 'Вакансий найдено', 'Вакансий обработано', 'Средняя зарплата'],
    ]
    for language, analysis in salaries.items():
        rows.append([
            language,
            analysis['vacancies_found'],
            analysis['vacancies_processed'],
            analysis['average_salary'],
        ])
    table = AsciiTable(rows, table_title)
    print(table.table)


def main():
    load_dotenv()
    superjob_key = os.getenv('SUPERJOB_KEY')
    salaries_sj = get_salaries_for_top_languages_sj(superjob_key)
    print_salaries_as_table(salaries_sj, table_title='SuperJob Moscow')

    salaries_hh = get_salaries_for_top_languages_hh()
    print_salaries_as_table(salaries_hh, table_title='HeadHunter Moscow')


if __name__ == "__main__":
    main()
