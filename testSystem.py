import sys
import os
from NLPWebPortal import app, db
from NLPWebPortal.model import TestQuery, Report
from NLPWebPortal.interpreter import interpret_query

def create_report():

  queries_to_run = TestQuery.query.all()

  for query in queries_to_run:

