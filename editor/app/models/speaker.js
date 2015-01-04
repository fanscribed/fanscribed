import DS from 'ember-data';

export default DS.Model.extend({

  sentences: DS.hasMany('sentence'),
  name: DS.attr('string')

});
