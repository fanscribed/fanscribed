import vanilla


class RobotsTxtView(vanilla.TemplateView):

    template_name = 'robots.txt'

    def render_to_response(self, context):
        response = super(RobotsTxtView, self).render_to_response(context)
        response['Content-Type'] = 'text/plain'
        return response
