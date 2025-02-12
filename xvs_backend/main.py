# Start Flask
#   cd to backend directory
#   1. env\Scripts\activate
#   2. flask run (debug mode will be off)
#      - py main.py (debug on)

# Stop Flask
#   1. ctrl+C
#   2. deactivate
from flask import Flask, request, session, jsonify
from html.parser import HTMLParser
from flask_cors import CORS
import re


app = Flask("__name__")
CORS(app)

class MyHTMLParser(HTMLParser):
  # RULE #1 - HTML Escape Before Inserting Untrusted Data into HTML Element Content
  htmlEscape = {"htmlEscape":"to escape special characters to prevent switching into execution context (some exceptions)",
                "*":"* in place of function if exception for complex attributes"}
  htmlEncoding = ["Escape the following characters with HTML entity encoding to prevent switching into any execution context",
                  "& --> &amp;", 
                  "< --> &lt;",
                  "> --> &gt;", 
                  "\" --> &quot;", 
                  "\' --> &#x27;", 
                  "/ --> &#x2F;",
                  "&apos; not recommended because its not in the HTML spec"]
  # RULE #2 - Attribute Escape Before Inserting Untrusted Data into HTML Common Attributes(html)
  htmlEscExcept = ["href", "src", "style", "events"]
  # Except for alphanumeric chars, escape all characters with ASCII values less than
  ##  256 with the &#xHH; format to prevent switching out of the attribute.
  # Unquoted attrs can be broken out of with many chars, including:
  breakChars = ["[space]", "%", "*", "+", ",", "-", "/", ";", "<", "=", ">", "^", "|"]
  # Validator.IsValidURL(userURL, 255)
  # if (isValidURL) { <a href = "<%=encoder.encodeForHTMLAttribute(userURL)%>" > link < /a >}

  # specify doc charset: <meta charset="utf-8">
  charset = {"charset": "(i.e. utf=8, ISO-8859-1) to prevent content interpretation vulnerabilities"}
  # RULE #3 - JavaScript Escape Before Inserting Untrusted Data into JavaScript Data Values
  jsEscape = {"jsEscape": "to escape special characters to prevent execution of malicious code",
              "*": "* in place of function if not for script tag"}
  # Except for alphanumeric chars, escape all characters less than 256 with
  ## the \xHH format to prevent switching out of the data value into the script
  ## context or into another attr. Do not use \" because the quote character may
  ## be matched by the HTML attr parser which runs first
  # breakChars the same
  eventHandlers = ["onabort", # hidden list
                   "onafterprint",
                   "onanimationend",
                   "onanimationiteration",
                   "onanimationstart",
                   "onbeforeprint",
                   "onbeforeunload",
                   "onblur",
                   "oncanplay",
                   "oncanplaythrough",
                   "onchange",
                   "onclick",
                   "oncontextmenu",
                   "oncopy",
                   "oncut",
                   "ondblclick",
                   "ondrag",
                   "ondragend",
                   "ondragenter",
                   "ondragleave",
                   "ondragover",
                   "ondragstart",
                   "ondrop",
                   "ondurationchange",
                   "onended",
                   "onerror",
                   "onfocus",
                   "onfocusin",
                   "onfocusout",
                   "onfullscreenchange",
                   "onfullscreenerror",
                   "onhashchange",
                   "oninput",
                   "oninvalid",
                   "onkeydown",
                   "onkeypress",
                   "onkeyup",
                   "onload",
                   "onloadeddata",
                   "onloadedmetadata",
                   "onloadstart",
                   "onmessage",
                   "onmousedown",
                   "onmouseenter",
                   "onmouseleave",
                   "onmousemove",
                   "onmouseover",
                   "onmouseout",
                   "onmouseup",
                   "onmousewheel",
                   "onoffline",
                   "ononline",
                   "onopen",
                   "onpagehide",
                   "onpageshow",
                   "onpaste",
                   "onpause",
                   "onplay",
                   "onplaying",
                   "onpopstate",
                   "onprogress",
                   "onratechange",
                   "onresize",
                   "onreset",
                   "onscroll",
                   "onsearch",
                   "onseeked",
                   "onseeking",
                   "onselect",
                   "onshow",
                   "onstalled",
                   "onstorage",
                   "onsubmit",
                   "onsuspend",
                   "ontimeupdate",
                   "ontoggle",
                   "ontouchcancel",
                   "ontouchend",
                   "ontouchmove",
                   "ontouchstart",
                   "ontransitionend",
                   "onunload",
                   "onvolumechange",
                   "onwaiting",
                   "onwheel", ]
  jsURIEscape = ["encodeURIComponent(", ]
  # RULE #3.1 - HTML escape JSON values in an HTML context and read the data with JSON.parse
  # Content-Type: application/json; charset=utf-8
  HTTPRequests = {"javascript": "XMLHttpRequest.getAllResponseHeaders()",
                  "jquery-ajax": "$.getJSON method only retreives data in JSON format",
                  "fetch": "set header: Content-Type : application/json"}
  ## htmlEscape json and parse with JSON.parse()
  # RULE #4 - CSS Escape And Strictly Validate Before Inserting Untrusted Data into HTML Style Property Values
  complexProps = ["url", "behavior", "custom"]
  urlUntrust = ["javascript:", "expression("]
  cssEscape = "CSS.escape("
  # RULE #5 - URL Escape Before Inserting Untrusted Data into HTML URL Parameter Values
  uriEscape = "encodeURI("
  # RULE #6 - Sanitize HTML Markup with a Library Designed for the Job
  # HtmlSanitizer
  # RULE #7 - Avoid JavaScript URL's
  inputAttrs = {"pattern":"to help with input validation.",
    "max":"to limit length of value if expecting specific value range", 
    "form":"ensures the data is submitted for the correct form"}
  
  def __init__(self):
    HTMLParser.__init__(self)
    self.data = []

  def handle_starttag(self, tag, attrs):
    # print(tag)
    # if(attrs):
    #   print(tag, "attributes : ")
    #   for attr in attrs:
    #     print("\tattribute :", attr[0], ", value :", attr[1])
    attrNames = [a[0] for a in attrs]

    # input validation
    if(tag == "input"): # change to regex to ensure attribute is set for each input attr while typing***
      print(attrs)
      if [True for i, a in enumerate(attrs) if a[0] == "type" and a[1] == "text"]:
        for attr in self.inputAttrs:
          if not attr in attrNames:
            fix = "%s attribute needed at line %d: %s" %(attr, self.getpos()[0], self.inputAttrs[attr])
            print(fix)
            self.data.append(fix)

    # charset configuration
    if(tag == "meta"):  # change to regex to ensure charset is set while typing***
      fix=[]
      print(fix)
      if(attrs):
        fix = [a[1] for a in attrs if a[0] == "charset"]
      
      if ( fix and fix[0] == None or "utf-8" not in fix): # check for possible charsets
        print(fix)
        fix = "charset attribute needed at line %d: %s" % (
            self.getpos()[0], self.charset["charset"])
        self.data.append(fix)

  def handle_startendtag(self, tag, attrs):
      print("Encountered an end tag :", tag)

  def escapeHelper(self, data, vulnVars, vulnStmt, vulnStr, escList, exceptions):
    untrust = False
    fix = []
    vulnFound = []
    for vulnVariable in vulnVars:
      reg = re.compile("var\s+"+vulnVariable +"\s*=\s*\w*\(*"+vulnStmt)
      vulnerable = reg.search(data)
      if(vulnerable):
        untrust = True
        vulnFound.append(vulnVariable)
        if(vulnFound):
          for es in escList:
            reg = re.compile("var\s+"+vulnVariable+"\s*=\s*" +
                             re.escape(es)+"\(\s*"+vulnStmt+"\)")
            vulnFixed = reg.search(data)
            if vulnFixed:
              untrust = False
    if(vulnFound):
      vulnFound = ", ".join(list(set(vulnFound))) + vulnStr + " block at line %d," % (self.getpos()[0])
      fix.append(vulnFound)
    if (untrust):
      for es in escList:
        fix.append("---> %s needed for variable: %s" % (
            es, escList[es]))
      if(exceptions):
        attrExcept = "    * Exceptions include: " + ", ".join(exceptions)
        fix.append(attrExcept)
      
      [fix.append(en) for en in self.htmlEncoding]
      
      fix = ["\n".join(fix)]
      self.data.extend(fix)

  def checkVulnScript(self, data, check):
    rule3ScriptCheck = "var\s+(\w+)\s*=\s*\w*document.createElement\(\s*[\'|\"]script[\'|\"]\s*\)"
    reg = re.compile(rule3ScriptCheck)
    vulnScripts = reg.findall(data)
    vulnVars = []
    exceptions = []
    if(vulnScripts):
      rule3ScriptCheck = ["\W"+ s + check for s in vulnScripts]
      for s in rule3ScriptCheck:
        reg = re.compile(s)
        vulnVars.extend(reg.findall(data))
    reg = re.compile(check)
    exceptionsCheck = reg.findall(data)
    if(exceptionsCheck):
      exceptions = [v  for v in exceptionsCheck if v not in vulnVars]
    
    return vulnVars, exceptions

  def checkVulnHTTP(self, data, vulnHTTP, vulnStr, getCheck, headerCheck):
    getReqs = []
    vuln = []
    fix = []
    for v in vulnHTTP:
      reg = re.compile(getCheck)
      req = reg.findall(data)
      getReqs.extend(req)
    if(getReqs):
      getReqs = list(set(getReqs))
      for r in getReqs:
        for h in headerCheck:
          reg = re.compile(r + h)
          setCheck = reg.search(data)
          if(setCheck):
            vuln.append(r)
            break
      vuln = [r for r in getReqs if r not in vuln]
      if(vuln):
        print(vuln)
        foundStr = ", ".join(list(set(vuln))) + vulnStr + " block at line %d," % (self.getpos()[0])
        fix.append(foundStr)
        fix.append("Content-Type check/set needed for HTTP request object.")
        for h in self.HTTPRequests:
          fix.append("---> %s: %s" % (
              h, self.HTTPRequests[h]))
        fix.append("Check Headers for \'Content-Type: application/json\', HTML escape response data")
        print(fix)
        fix = ["\n".join(fix)]
        self.data.extend(fix)

      # headerChecks = []
      # for r in getReqs:
      #   reg = re.compile(v + headerCheck)
      #   req = reg.findall(data)
      #   headerChecks.extend(req)
      # print(headerChecks)
    

  def handle_data(self, data):
    # print(data)

    # Never Do
    "<script > ...NEVER PUT UNTRUSTED DATA HERE... < /script >"
    "<!--...NEVER PUT UNTRUSTED DATA HERE...-->"
    "<div ...NEVER PUT UNTRUSTED DATA HERE...=test />"
    "<NEVER PUT UNTRUSTED DATA HERE... href=\"/test\" />"
    "<style >...NEVER PUT UNTRUSTED DATA HERE...</style >"
    "<script >window.setInterval('...EVEN IF YOU ESCAPE UNTRUSTED DATA YOU ARE XSSED HERE...')</script >"

    # Rule 1: Inserting untrusted data into HTML element content
    rule1Str = " vulnerable to HTML element content injection:"
    rule1Check = "document.getElementBy\w+\(\"\S+\"\).(?:innerHTML|text)\s*=\s*(.*?)(?:\s|$|;)"
    escStmt = "document.getElementBy\S+\.value"
    reg = re.compile(rule1Check)
    vulnVars = reg.findall(data)
    if(vulnVars):
      self.escapeHelper(data, vulnVars, escStmt, rule1Str, self.htmlEscape, [])

    # Rule 2: Inserting untrusted data into attr
    rule2Str = " vulnerable to attribute injection:"
    rule2Check = "document.getElementBy\w+\(\"\S+\"\).setAttribute\(\S+,\s?(\w+)\)(?:\s|$|;)"
    reg = re.compile(rule2Check)
    vulnVars = reg.findall(data)
    if(vulnVars):
      self.escapeHelper(data, vulnVars, escStmt, rule2Str, self.htmlEscape, self.htmlEscExcept)

    # Rule 3: Inserting Untrusted Data into DYNAMIC JavaScript Data Values
    rule3Str = " vulnerable to dynamic javascript injection:"
    rule3Exc = " may be vulnerable to dynamic javascript injection (if for script tag):"

    ## vulnerable quoted string
    quotedStringCheck = r"\.innerHTML\s*=\s*\"alert\(\\[\'|\"]\"\+(\w+)"
    vulnVars, scriptExcept = self.checkVulnScript(data, quotedStringCheck)
    if(vulnVars):
      self.escapeHelper(data, vulnVars, escStmt, rule3Str, self.jsEscape, [])
    if(scriptExcept):
      self.escapeHelper(data, scriptExcept, escStmt, rule3Exc, self.jsEscape, [])

    ## vulnerable quoted expr
    quotedExprCheck = r"\.innerHTML\s*=\s*\"\w+=\\[\'|\"]\"\+(\w+)"
    vulnVars, scriptExcept = self.checkVulnScript(data, quotedExprCheck)
    if(vulnVars):
      self.escapeHelper(data, vulnVars, escStmt, rule3Str, self.jsEscape, [])
    if(scriptExcept):
      self.escapeHelper(data, scriptExcept, escStmt, rule3Exc, self.jsEscape, [])

    ## vulnerable quoted event handler
    vulnEvents = []
    for event in self.eventHandlers:  
      quotedEventCheck = r"document.getElementBy\w+\S+\."+event+r"\s*=\s*\"\w+=\\[\'|\"]\"\+(\w+)"
      reg = re.compile(quotedEventCheck)
      vuln = reg.findall(data)
      if(vuln):
        vulnEvents.extend(vuln)
    if(vulnEvents):
      self.escapeHelper(data, vulnEvents, escStmt, rule3Str, self.jsEscape, [])
    
    # Rule 3.1 HTML escape JSON values in HTML context: read data with JSON.parse (http response)
    ## js http request
    vulnHTTPStr = " may be vulnerable to XSS"
    HTTPObjectCheck = "const\s+(\w+)\s*=\s*new\s+XMLHttpRequest"
    HTTPGetCheck = "(\w+)\.open\(\"GET" # start string with http object
    HTTPCheckHeaders = ["\.getAllResponseHeaders", 
                        "\.responseType\s*=\s*\'json\'",
                        "\.setRequestHeader\(\s*\'Content-Type'\s*,\s*\'application/json\'"]  # start string with http object
    reg = re.compile(HTTPObjectCheck)
    vulnHTTP = reg.findall(data)
    if(vulnHTTP):
      self.checkVulnHTTP(data, vulnHTTP, vulnHTTPStr, HTTPGetCheck, HTTPCheckHeaders)

  # def handle_endtag(self, tag):
  #    print(tag)


@app.route("/")
def index(): 
  return "<h1>Flask Running</h1>"



@app.route("/analyze", methods=["POST", "GET"])
def analyze():
  parser = MyHTMLParser()
  if request.method == "POST":
    print("\nRecieved POST Request\n")
    content = request.get_json()

    print("Data:\n" + content["data"] + "\n")
    parser.feed(content["data"])
    if(parser.data):
      session["data"] = parser.data
    else:
      session["data"] = ["no vulnerabilities analyzed"]

    return jsonify({"status": "Post Request Success", "data": session["data"]})

  if request.method == "GET":
    print("Recieved GET Request")
    print(session.get("data"))

    return jsonify({"status": "GET Request Success", "data": content})

  return "Analyzing..."


if __name__ == "__main__":
    app.secret_key = 'super secret key'
    # app.config['SESSION_TYPE'] = 'filesystem'
    app.debug = True
    app.run()



# Installed:
#   py -m pip install -U autopep8
#   pip install html.parser 
#   pip install -U flask-cors
