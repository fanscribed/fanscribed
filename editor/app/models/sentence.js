import DS from 'ember-data';

export default DS.Model.extend({

  transcript: DS.belongsTo('transcript'),

  latest_text: DS.attr('string'),
  latest_start: DS.attr('number'),
  latest_speaker: DS.belongsTo('speaker')

});
