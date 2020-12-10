from nameko.rpc import rpc, RpcProxy


class Filter:
    """Microservice for filtering top events"""
    # Vars

    name = 'filter'
    top_das_rpc = RpcProxy('top_das')
    event_das_rpc = RpcProxy('event_das')
    logger_rpc = RpcProxy('logger')

    # Logic

    # API

    @rpc
    def get_events(self, user, tags):
        """Getting tags, sending filtered events back
        :params:
            user - user login or None
            tags - list of tags
        :returns:
            filtered_events - filtered top user's events"""

        if 'online' in tags:
            is_online = True
            tags.remove('online')
        else:
            is_online = False

        if 'paid' in tags:
            is_paid = True
            tags.remove('paid')
        else:
            is_paid = False

        tags = set(tags)

        if user is None:
            events = self.event_das_rpc.get_events_by_date()
        else:
            top_events = self.top_das_rpc.get_top(user)

            events = list()
            for event_id in top_events:
                events.append(self.event_das_rpc.get_event_by_id(event_id))
        self.logger_rpc.log(self.name, self.get_events.__name__, [
                            user, list(tags)], "Info", "Filtering events")

        if not len(tags):
            return events

        if not len(tags):
            if is_online or is_paid:
                filtered_events = events
            else:
                return events
        else:
            filtered_events = list()
            for event in events:
                event_tags = set(event['tags'])
                if len(tags & event_tags):
                    filtered_events.append(event)

        # in order to only get events with these tags
        # if they are presented in filter tags
        if is_online:
            tmp_filtered_events = filtered_events.copy()
            for event in tmp_filtered_events:
                event_tags = event['tags']
                if 'online' not in event_tags:
                    filtered_events.remove(event)
        if is_paid:
            tmp_filtered_events = filtered_events.copy()
            for event in tmp_filtered_events:
                event_tags = event['tags']
                if 'paid' not in event_tags:
                    filtered_events.remove(event)

        return filtered_events
