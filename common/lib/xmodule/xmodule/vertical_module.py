from xblock.fragment import Fragment
from xmodule.x_module import XModule, STUDENT_VIEW
from xmodule.seq_module import SequenceDescriptor
from xmodule.progress import Progress
from xmodule.studio_editable import StudioEditableModule, StudioEditableDescriptor
from pkg_resources import resource_string
from copy import copy
from xblock.core import XBlock


# HACK: This shouldn't be hard-coded to two types
# OBSOLETE: This obsoletes 'type'
class_priority = ['video', 'problem']


class VerticalFields(object):
    has_children = True


class VerticalModule(VerticalFields, XModule, StudioEditableModule):
    ''' Layout module for laying out submodules vertically.'''

    def __init__(self, *args, **kwargs):
        super(VerticalModule, self).__init__(*args, **kwargs)

        self.update_names()

    def update_names(self):
        """
        Updates old vertical names with new.

        Use case: when one has edited Group Configuration page in split test module,
        verticals are not updated automatically. 
        This is done for the old courses, where already exists difference between vertical names
        stored in group configuration data and vertical names, stored in vertical xfields.
        """
        parent = self.get_parent_xblock()
        if getattr(parent, 'get_display_name_for_vertical'):
            updated_name = parent.get_display_name_for_vertical(self)
            if updated_name:
                self.display_name = updated_name
                user_id = self.descriptor.runtime.service(self.descriptor, 'user').user_id
                self.descriptor.runtime.modulestore.update_item(self.descriptor, user_id)

    def get_parent_xblock(self):
        """
        Get parent xblock for the current xblock.
        """
        parent_location = self.descriptor.runtime.modulestore.get_parent_location(self.location)
        return self.descriptor.runtime.modulestore.get_item(parent_location)

    def student_view(self, context):
        fragment = Fragment()
        contents = []

        child_context = {} if not context else copy(context)
        child_context['child_of_vertical'] = True

        for child in self.get_display_items():
            rendered_child = child.render(STUDENT_VIEW, child_context)
            fragment.add_frag_resources(rendered_child)

            contents.append({
                'id': child.location.to_deprecated_string(),
                'content': rendered_child.content
            })

        fragment.add_content(self.system.render_template('vert_module.html', {
            'items': contents,
            'xblock_context': context,
        }))
        return fragment

    def author_view(self, context):
        """
        Renders the Studio preview view, which supports drag and drop.
        """
        fragment = Fragment()
        root_xblock = context.get('root_xblock')
        is_root = root_xblock and root_xblock.location == self.location

        # For the container page we want the full drag-and-drop, but for unit pages we want
        # a more concise version that appears alongside the "View =>" link-- unless it is
        # the unit page and the vertical being rendered is itself the unit vertical (is_root == True).
        if is_root or not context.get('is_unit_page'):
            self.render_children(context, fragment, can_reorder=True, can_add=True)
        return fragment

    def get_progress(self):
        # TODO: Cache progress or children array?
        children = self.get_children()
        progresses = [child.get_progress() for child in children]
        progress = reduce(Progress.add_counts, progresses, None)
        return progress

    def get_icon_class(self):
        child_classes = set(child.get_icon_class() for child in self.get_children())
        new_class = 'other'
        for c in class_priority:
            if c in child_classes:
                new_class = c
        return new_class


@XBlock.wants('user')
class VerticalDescriptor(VerticalFields, SequenceDescriptor, StudioEditableDescriptor):
    """
    Descriptor class for editing verticals.
    """
    module_class = VerticalModule

    js = {'coffee': [resource_string(__name__, 'js/src/vertical/edit.coffee')]}
    js_module_name = "VerticalDescriptor"

    # TODO (victor): Does this need its own definition_to_xml method?  Otherwise it looks
    # like verticals will get exported as sequentials...

    @property
    def non_editable_metadata_fields(self):
        non_editable_fields = super(VerticalDescriptor, self).non_editable_metadata_fields
        non_editable_fields.extend([
            VerticalDescriptor.due,
        ])
        return non_editable_fields
