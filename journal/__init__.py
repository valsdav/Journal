from flask import Flask

app = Flask(__name__,instance_relative_config=True)
app.config.from_object('journal.config')

import journal.journal_ui
import journal.journal_api
