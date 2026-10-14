from os import sep
from app.lib.bottle import Bottle, request, response, static_file
import re

static_app = Bottle()

@static_app.error(404)
def error404(error):
    response.status = 404
    return """
      Page not found! <a href="/app/payroll/web/portal">
        Click Here
      </a>
    """


@static_app.route("/payroll/web/<filename:path>")
def static_path(filename):
  if filename == "portal":
    filename = "index.html"

  header = request.headers

  min_ver = 80 # this will increase soon for compatibility browser

  if not 'User-Agent' in header:
    return f'''
      <html>
        <body style="background-color: black;">
          <b style="color: white;">Update your chrome browser to latest version: minimum requirements: is chrome {min_ver} !</style>
        </body>
      </html>
    '''

  return static_file(filename = filename, root = f"data{sep}webapp{sep}web")
  # user_agent = header['User-Agent'].lower()

  
  # if not 'chrome' in user_agent:
  #   return f'''
  #     <html>
  #       <body style="background-color: black;">
  #         <b style="color: white;">Update your chrome browser to latest version: minimum requirements: is chrome {min_ver} !</style>
  #       </body>
  #     </html>
  #   '''

  # try:
  #   pos = user_agent.find('chrome')

  #   step1 = user_agent[pos:]

  #   step2 = step1[:step1.find('.')]

  #   device, version = step2.split('/')

    
  #   if int(version) < min_ver:
  #     return f'''
  #       <html>
  #         <body style="background-color: black;">
  #           <b style="color: white;">Update your chrome browser to latest version: minimum requirements: is chrome {min_ver} !</style>
  #         </body>
  #       </html>
  #     '''

  #   return static_file(filename = filename, root = f"data{sep}webapp{sep}web")
  # except Exception as er:
  #   print(er)

  