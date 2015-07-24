import Decimal from 'decimal.js';
import React from 'react';


function zeroPadded (s, length = 2) {
  while (s.length != length) {
    s = '0' + s;
  }
  return s;
}


export default class Timecode extends React.Component {

  static propTypes = {
    time: React.PropTypes.objectOf(Decimal).isRequired,
  }

  render() {
    let hours = this.props.time.divToInt(60 * 60);
    let minutes = this.props.time.divToInt(60).mod(60);
    let seconds = this.props.time.floor().mod(60);
    let hundredths = this.props.time.times(100).floor().mod(100);

    let h = hours.toString();
    let m = zeroPadded(minutes.toString());
    let s = zeroPadded(seconds.toString());
    let hs = zeroPadded(hundredths.toString());

    return <span>{h}:{m}:{s}.{hs}</span>;
  }

}