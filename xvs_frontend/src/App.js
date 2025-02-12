import React from 'react';
import './App.css';
import InputHTML from './components/InputHTML.js';

class App extends React.Component {
  constructor(props) {
    super(props);

    this.state = {
      inputPlaceHolder: 
        "Enter Input Here",
      preview: "Preview",
      output: ["Vulnerabilities Will be Populated Here"],
    }

    this.handleInput = this.handleInput.bind(this);
  }

  async handleInput(event) {
    var data = event.target.value;

    this.setState({
      preview: data,
    });

    var response = await fetch('http://127.0.0.1:5000/analyze', {
      method: "post",
      mode: 'cors', // cors, *cors, same-origin
      headers: { 
        'Content-Type': 'application/json' },
      body: JSON.stringify({"data": data})
    }).then(function (response) {
      return response.json();
    }).catch(function(err){
      console.log(err)
    });
    console.log(await response)

    this.setState({
      output: await response.data,
    })
  }

  render() {
    return (
      <div className="App">
        <header className="App-header">
          <div className="header">
            <h1 className="header">XSS Vulnerability Scanner</h1>
            <p>Enter HTML to be analyzed</p>
          </div>
          <div className="main">
            <InputHTML data={this.state} handleInput={this.handleInput} />
            <div style={htmlStyle}>{this.state.output.map(output => (
              <div className="output" style={{ paddingBottom: "5%"}} key={output}>{output}</div>
            ))}</div>

          </div>
        </header>
      </div>
    );
  }
}

export default App;
//under main
//{/**/}
//

const htmlStyle = {
  whiteSpace: "pre-wrap",
  wordWrap: "break-word",
  height: "45vh",
  width: "40vw",
  border: "medium solid green",
  borderLeftWidth: "thin",
  textAlign: "left",
  fontFamily: '"Fira code", "Fira Mono", monospace',
  fontSize: 12,
  resize: "both",
  overflow: "auto",
  paddingLeft: "2%",
  textIndent: "-4%",
}

