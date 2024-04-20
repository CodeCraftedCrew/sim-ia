class RelationHandler:

    @staticmethod
    def filter_relations(relations, restrictions):
        relations_by_type = {}
        for relation in relations.values():

            type_tag = relation.tags.get("type", None)

            if type_tag and type_tag.value in restrictions:
                relationsx = relations_by_type.get(type_tag.value, [])
                relationsx.append(relation)
                relations_by_type[type_tag.value] = relationsx

        return relations_by_type

    @staticmethod
    def map_restrictions_by_direction(restrictions):

        left, right, straight = True, True, True

        for restriction in restrictions:

            if restriction == "no_left_turn":
                left = False

            elif restriction == "no_right_turn":
                right = False

            elif restriction == "no_straight_on":
                straight = False

            elif restriction == "only_left_turn":
                right = False
                straight = False

            elif restriction == "only_right_turn":
                left = False
                straight = False

            elif restriction == "only_straight_on":
                right = False
                left = False

        return left, right, straight

    @staticmethod
    def extract_members(restriction):
        from_member = None
        to_member = None
        via_member = None
        for member in restriction.members:
            if member.role == "from":
                from_member = member
            elif member.role == "to":
                to_member = member
            elif member.role == "via":
                via_member = member
        return from_member, to_member, via_member

    @staticmethod
    def add_restriction(restriction_dict, from_id, via_id, to_id, restriction_value):
        from_restrictions = restriction_dict.get(from_id, {})
        via_restrictions = from_restrictions.get(via_id, {})
        via_restrictions[to_id] = via_restrictions.get(to_id, []) + [restriction_value]
        from_restrictions[via_id] = via_restrictions
        restriction_dict[from_id] = from_restrictions

    @staticmethod
    def map_restrictions(restrictions):
        mapped_restrictions = {}
        via_as_way_restrictions = {}

        for restriction in restrictions:
            from_member, to_member, via_member = RelationHandler.extract_members(restriction)

            if not from_member or not to_member or not via_member:
                continue

            restriction_value = restriction.tags["restriction"].value

            if via_member.type == "w":
                RelationHandler.add_restriction(via_as_way_restrictions, via_member.id, from_member.id, to_member.id,
                                          restriction_value)
            else:
                RelationHandler.add_restriction(mapped_restrictions, from_member.id, via_member.id, to_member.id,
                                          restriction_value)

        return mapped_restrictions, via_as_way_restrictions