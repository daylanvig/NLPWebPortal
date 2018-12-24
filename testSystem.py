import sys
import os
import random
import colorama
from termcolor import cprint
from sqlalchemy import func
from NLPWebPortal import app, db
from NLPWebPortal.model import TestQuery, TestResult, Report, User, TrainingFile, Dictionary, Query, UserQuery
from NLPWebPortal.interpreter import interpret_query
import warnings
from sqlalchemy.exc import SAWarning


def switch(selection):
  switch = {
      1: view_existing_queries,
      2: new_test_query,
      3: view_reports,
      4: new_report,
      5: maintain_accounts,
      0: exit
  }
  command = switch.get(selection)
  command()


def start():
  """
  Loads the menu of available options
  
  """
  colorama.init()
  warnings.filterwarnings('ignore', r".*support Decimal objects natively",
                          SAWarning, r'^sqlalchemy\.sql\.sqltypes$')
  options = [0, 1, 2, 3, 4, 5]
  print(' ')
  print('Select from the following options:')
  print(' ')
  print(' [1]  View existing test queries')
  print(' [2]  Create new test query')
  print(' [3]  View test reports')
  print(' [4]  Run test now')
  print(' [5]  Maintain user accounts')
  print(' [0]  Exit')
  print(' ')
  while True:
    try:
      selected = int(input('Selection: '))  #TODO: Error handle
      while (selected not in options):
        print('Invalid option, try again: ')
        selected = int(input('Selection: '))
      break
    except:
      print('Invalid selection. You must choose a number from 0-5')
  switch(selected)


def new_test_query():
  query = input("Fragmented Query: ")
  result = input("Expected Result: ")
  tq = TestQuery(query, result)
  db.session.add(tq)
  db.session.commit()
  print('Success!')
  print(' [1]   Add another query')
  print(' [2]   Return to main menu')
  print(' [0]   Exit')
  selected = int(input('Selection: '))
  while (selected not in [0, 1, 2]):
    print('Invalid option, try again: ')
    selected = int(input('Selection: '))
  if selected == 1:
    new_test_query()
  elif selected == 2:
    start()
  else:
    exit()


def view_existing_queries():
  query_list = db.session.query(TestQuery).all()
  for q in query_list:
    print(q)
  print(' ')
  print(' [1]   Maintain query')
  print(' [2]   Return to main menu')
  print(' [0]   Exit')
  selected = int(input("Selection: "))
  while (selected not in [0, 1, 2]):
    print('Invalid option, try again: ')
    selected = int(input('Selection: '))
  if selected == 1:
    query_selected = int(input('Enter the query number to maintain: '))
    query = db.session.query(TestQuery).filter(
        TestQuery.query_id == query_selected).first()
    if query:
      print(' ')
      print(query.detailed())
      print(' ')
      print(' [1]   Delete Query')
      print(' [2]   Change Fragment')
      print(' [3]   Change Expected Result')
      print(' [4]   Return to Main Menu')
      print(' [0]   Exit')
      print(' ')
      selected = int(input('Selection: '))
      while selected not in [0, 1, 2, 3, 4]:
        print('Invalid option, try again: ')
        selected = int(input('Selection: '))
      if selected == 1:
        db.session.delete(query)
        db.session.commit()
      elif selected == 2:
        query.query_text = input('Fragment: ')
      elif selected == 3:
        query.results_expected = input('Expected: ')
      elif selected == 4:
        start()
      elif selected == 0:
        exit()
    else:
      print(' ')
      print('Invalid query!')
      view_existing_queries()
  elif selected == 2:
    start()
  else:
    exit()


def view_reports():
  report_list = db.session.query(Report).all()
  if len(report_list) == 0:  # No reports saved
    cprint('No reports exist.\n', 'red')
    print(' [1]   Create report')
    print(' [2]   Return to main menu')
    print(' [0]   Exit\n')
    selected = int(input('Selection: '))
    while (selected not in [0, 1, 2]):
      print('Invalid option, try again: ')
      selected = int(input('Selection: '))
    if selected == 1:
      new_report()
    elif selected == 2:
      start()
    else:
      exit()
  else:
    for r in report_list:
      print(r)
    print(' ')
    print(' [1]   Detailed report')
    print(' [2]   Return to main menu')
    print(' [0]   Exit')
    print(' ')
    selected = int(input('Selection: '))
    while (selected not in [0, 1, 2]):
      print('Invalid option, try again: ')
      selected = int(input('Selection: '))
    if selected == 1:
      report_selected = int(input('Enter the report number to maintain: '))
      report = db.session.query(Report).filter(
          Report.report_id == report_selected).first()
      if report:
        print(' ')
        print(report.detailed())
        print(' ')
        print(' [1]   Select Another Report')
        print(' [2]   Return to Main Menu')
        print(' [0]   Exit')
        print(' ')
        selected = int(input('Selection: '))
        while selected not in [0, 1, 2]:
          print('Invalid option, try again: ')
          selected = int(input('Selection: '))
        if selected == 1:
          view_reports()
        elif selected == 2:
          start()
        elif selected == 0:
          exit()
      else:
        print(' ')
        print('Invalid query!')
        view_existing_queries()
    elif selected == 2:
      start()
    else:
      exit()


def run_tests(selected_tests):

  print('How would you like test results to be evaluated? ')
  print(' [1]   Manual Evaluation (Recommended)')
  print(' [2]   Automatic Evaluation (Experimental. Not Recommended)')
  automatic = int(input('Selection: '))
  while automatic not in [1, 2]:
    print('Invalid selection, try again.')
    automatic = int(input('Selection: '))
  if automatic == 1:
    manual = True
  else:
    manual = False

  queries = []
  #Create report and commit so key is generated to be used as fKey in tests
  report = Report(manual)
  db.session.add(report)
  db.session.commit()

  for t in selected_tests:  # Get selected queries from database
    queries.append(
        db.session.query(TestQuery).filter(TestQuery.query_id == t).first())

  for q in queries:  # Run tests on queries
    result = interpret_query(None, q.query_text, False)
    tr = TestResult(q.query_id, report.report_id, result)
    db.session.add(tr)

  # Store results, calculate accuracy, commit.
  db.session.commit()
  report.accuracy_calculate()
  db.session.commit()

  # Print summary of report
  cprint('Report complete!\n', 'green')
  print(report)


def new_report():
  print(' ')
  print('Generate Report:')
  print(' ')
  print(' [1]   Select Tests')
  print(' [2]   Use Random Tests')
  print(' [3]   Run All Tests')
  print(' [4]   Return to Main Menu')
  print(' [0]   Exit')
  print(' ')
  selected = int(input('Selection: '))
  while (selected not in [0, 1, 2, 3, 4]):
    print('Invalid option, try again: ')
    selected = int(input('Selection: '))
  if selected == 1:  # * Choose tests
    all_tests = []
    selected_test = int(input('Enter test query number: '))
    while (selected_test != 0):
      all_tests.append(selected_test)  # TODO: Verify test is valid
      selected_test = int(
          input(
              'Enter another test number or press \'0\' to run selected tests'))
    if len(all_tests) == 0:
      print('Error: No tests selected.')
      new_report()
    else:
      run_tests(all_tests)
      print('')
      print(' [1]   Return to Main Menu')
      print(' [0]   Exit')
      print(' ')
      selected = int(input('Selection:'))
      while selected not in [0, 1]:
        print('Invalid selection, try again.')
        selected = int(input('Selection: '))
      if selected == 1:
        start()
      else:
        exit()
  elif selected == 2:  # * Random tests
    print(' ')
    n_max = db.session.query(func.max(TestQuery.query_id)).scalar()
    print('There are %d test queries available.') % (n_max)
    n_tests = int(
        input('How many tests would you like to run?'))  #TODO Escape sequence
    while (n_tests < 1 or n_tests > n_max):
      n_tests = int(
          input(
              'Invalid selection try again. Selection must be greater than 0 and elss than %d'
          )) % (
              n_max)
    available_tests = list(range(1, n_max + 1))
    random.shuffle(available_tests)
    selected_tests = []
    for n in range(n_tests):
      selected_tests.append(available_tests.pop())
    run_tests(selected_tests)
  elif selected == 3:  # * All tests
    n_max = db.session.query(func.max(TestQuery.query_id)).scalar()
    all_tests = list(range(1, n_max + 1))
    run_tests(all_tests)
  elif selected == 4:
    start()
  else:
    exit()


def maintain_accounts():  #TODO Maybe make this a thing
  r = db.session.query(Report).all()
  for a in r:
    db.session.delete(a)
  u = db.session.query(User).all()
  for a in u:
    db.session.delete(a)
  u = db.session.query(TrainingFile).all()
  for a in u:
    db.session.delete(a)
  u = db.session.query(Dictionary).all()
  for a in u:
    db.session.delete(a)
  u = db.session.query(Query).all()
  for a in u:
    db.session.delete(a)
  u = db.session.query(UserQuery).all()
  for a in u:
    db.session.delete(a)
  u = db.session.query(TestQuery).all()
  for a in u:
    db.session.delete(a)
  u = db.session.query(TestResult).all()
  for a in u:
    db.session.delete(a)
  db.session.commit()


if __name__ == '__main__':
  start()
