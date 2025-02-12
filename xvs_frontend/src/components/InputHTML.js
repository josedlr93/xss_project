import React from 'react';
import Editor from 'react-simple-code-editor';
import { highlight, languages } from 'prismjs/components/prism-core';
import 'prismjs/components/prism-clike';
import 'prismjs/components/prism-javascript';
import 'prismjs/components/prism-markup';

class InputHTML extends React.Component {
  constructor(props) {
    super(props);

    this.state = {
      value: this.props.data.inputPlaceHolder,
    };

    //bindings
  }
    
  render() {
    return (
      <Editor
        value={this.state.value}
        placeholder="Enter Input Here"
        onValueChange={code => this.setState({ value: code })}
        highlight={code => highlight(code, languages.js)}
        onChange={this.props.handleInput}
        padding={10}
        style={textAreaStyle}
      />
      
    );
  }
}

export default InputHTML;
  
const textAreaStyle = {
  height: "45.6vh",
  width: "40vw",
  whiteSpace: "pre-line",
  wordWrap: "break-word",
  border: "medium solid green",
  fontFamily: '"Fira code", "Fira Mono", monospace',
  fontSize: 12,
  rows: 100,
  resize: "both",
  overflow:"auto"
}