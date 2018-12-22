import sys
import os
from NLPWebPortal import app, db
from NLPWebPortal.model import TestQuery, Report, User
from NLPWebPortal.interpreter import interpret_query


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
  selected = int(input('Selection: '))  #TODO: Error handle
  while (selected not in options):
    print('Invalid option, try again: ')
    selected = int(input('Selection: '))
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


def new_report():
  print('s')


def maintain_accounts():
  print('a')


if __name__ == '__main__':
  start()
