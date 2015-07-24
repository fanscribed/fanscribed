import Decimal from 'decimal.js';
import React from 'react';

import Timeline from './Timeline.jsx';

export default class Editor extends React.Component {

  render() {
    let transcript = this.props.transcript;
    let length = new Decimal(transcript.length);
    return (
      <div>
        <h1>{transcript.title}</h1>
        <Timeline
          length={length}
          />
      </div>
    );
  }

}
