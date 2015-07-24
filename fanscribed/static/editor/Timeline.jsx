import Decimal from 'decimal.js';
import R from 'ramda';
import React from 'react';

import { range } from './decimalRange';
import Timecode from './timecode.jsx';

class Timeframe extends React.Component {

  static propTypes = {
    start: React.PropTypes.objectOf(Decimal).isRequired,
  }

  render() {
    return (
      <div>
        <Timecode time={this.props.start} />
      </div>
    );
  }

}

export default class Timeline extends React.Component {

  static defaultProps = {
    step: new Decimal(10),
  }

  static propTypes = {
    length: React.PropTypes.objectOf(Decimal).isRequired,
  }

  render() {
    var start = new Decimal(0);
    var length = this.props.length;
    var step = this.props.step;
    return (
      <div>
        <ul>
          <li>Length: <Timecode time={length} /></li>
        </ul>
        {
          R.map(
            (time) => <Timeframe start={time} key={time} />,
            range(start, length, step)
          )
        }
      </div>
    );
  }

}