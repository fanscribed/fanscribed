import DS from 'ember-data';

export default DS.Model.extend({

  url: DS.attr('string'),
  title: DS.attr('string'),
  state: DS.attr('string'),
  length: DS.attr('number'),
  length_state: DS.attr('string'),

  sentences: DS.hasMany('sentence'),

  slug: function () {
    // http://stackoverflow.com/a/1054862/72560
    return this.get('title')
      .toLowerCase()
      .replace(/[^\w ]+/g,'')
      .replace(/ +/g,'-')
      ;
  }.property('title'),

  detailUrl: function() {
    return '/transcripts/' + this.get('id') + '-' + this.get('slug') + '/';
  }.property('slug')

});
