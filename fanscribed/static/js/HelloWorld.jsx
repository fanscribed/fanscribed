import React from 'react';

var HelloWorld = React.createClass({

  render() {
    return <div>Hello {this.props.name}</div>;
  }

});

module.exports = HelloWorld;
