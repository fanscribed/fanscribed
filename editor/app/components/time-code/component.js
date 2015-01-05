import Ember from 'ember';
import numeral from 'numeral';

export default Ember.Component.extend({

  hoursMinutesSeconds: function() {
    return numeral(this.get('time')).format('00:00:00.00');
  }.property('time'),

  hundredths: function() {
    var time = this.get('time');
    var hundredths = (time - Math.floor(time));
    return numeral(hundredths).format('.00');
  }.property('time')

});
