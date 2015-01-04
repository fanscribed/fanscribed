import DS from 'ember-data';

export default DS.Model.extend({
  url: DS.attr('string'),
  title: DS.attr('string'),
  state: DS.attr('string'),
  length: DS.attr('number'),
  length_state: DS.attr('string')
});
