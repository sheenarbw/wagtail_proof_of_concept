from django.db import models

from wagtail.core.models import Page, Orderable
from wagtail.core.fields import RichTextField,StreamField
# from wagtail.images.edit_handlers import ImageChooserPanel
from wagtail.admin.edit_handlers import FieldPanel, InlinePanel,PageChooserPanel
from wagtail.core.models import Page
from wagtail.core import blocks
from wagtail.admin.edit_handlers import FieldPanel, StreamFieldPanel
from wagtail.images.blocks import ImageChooserBlock
# from wagtailmarkdown.edit_handlers import MarkdownPanel
# from wagtailmarkdown.fields import MarkdownField
from modelcluster.fields import ParentalKey
from wagtail.admin.edit_handlers import FieldPanel, InlinePanel,PageChooserPanel
# from wagtail.snippets.models import register_snippet

def _id_gen():
    i = 0
    while True:
        yield f"block_{i}"
        i+=1

id_generator = _id_gen()

class HomePage(Page):
    body = RichTextField(blank=True)

    content_panels = Page.content_panels + [
        FieldPanel('body', classname="full"),
    ]

    subpage_types=['NewsIndexPage','ClubIndexPage','CurriculumIndexPage','CurriculumContentItemDirectoryIndexPage',]


class NewsIndexPage(Page):
    intro = RichTextField(blank=True)

    content_panels = Page.content_panels + [
        FieldPanel('intro', classname="full")
    ]

    subpage_types = ['NewsItemPage']


class NewsItemPage(Page):
    description = RichTextField(blank=True)
    body = RichTextField(blank=True)
    subpage_types=[]
    date = models.DateField()

    content_panels = Page.content_panels + [
        FieldPanel('date', classname="full"),
        FieldPanel('description', classname="full"),
        FieldPanel('body', classname="full"),
    ]


class ClubIndexPage(Page):
    intro = RichTextField(blank=True)

    content_panels = Page.content_panels + [
        FieldPanel('intro', classname="full")
    ]

    subpage_types = ['ClubPage']


class ClubPage(Page):
    description = RichTextField(blank=True)
    whatsapp_group_link = models.URLField(blank=True, null=True)
    calendar_link = models.URLField(blank=True, null=True)
    subpage_types=[]



class CurriculumIndexPage(Page):
    subpage_types = ['CurriculumPage']



class CurriculumPage(Page):
    body = RichTextField(blank=True)
    nqf_standard = models.CharField(max_length=5,blank=True,null=True)
    full_time_duration_months = models.SmallIntegerField(default=9)

    content_items = models.ManyToManyField("CurriculumContentItem", through="CurriculumContentRequirement", related_name="curriculums",symmetrical=False,)

    content_panels = Page.content_panels + [
        InlinePanel('curriculum_requirements', label="content items"),
        FieldPanel('body', classname="full"),
        FieldPanel('nqf_standard'),
        FieldPanel('full_time_duration_months')
    ]

    subpage_types=[]




class CurriculumContentRequirement(Orderable):
    curriculum = ParentalKey("CurriculumPage", on_delete=models.CASCADE, related_name="curriculum_requirements")

    content_item = ParentalKey("CurriculumContentItem", on_delete=models.PROTECT,related_name="curriculum_requirements")
    hard_requirement = models.BooleanField(default=True)


class ContentItemOrder(Orderable):
    post = ParentalKey(
        "CurriculumContentItem", on_delete=models.PROTECT, related_name="pre_ordered_content"
    )
    pre = ParentalKey(
        "CurriculumContentItem", on_delete=models.PROTECT, related_name="post_ordered_content"
    )
    hard_requirement = models.BooleanField(default=True)

    class Meta:
        unique_together = [["pre", "post"]]

    @property
    def pre_title(self):
        return self.pre.title

    @property
    def post_title(self):
        return self.post.title


    panels = [
        PageChooserPanel('pre'),
        PageChooserPanel('post'),
        FieldPanel('hard_requirement'),
    ]





class CurriculumContentItemDirectoryIndexPage(Page):
    subpage_types=['CurriculumContentItemDirectory']

class CurriculumContentItemDirectory(Page):
    subpage_types=['CurriculumContentItemDirectory','CurriculumContentItem']


class HeadingBlock(blocks.StructBlock):
    heading = blocks.CharBlock(form_classname="full title")
    level = blocks.IntegerBlock(min_value=1,max_value=4)



class FlipCardBlock(blocks.StructBlock):
    front = blocks.RichTextBlock()
    back = blocks.RichTextBlock()

    class Meta:
        template = 'home/blocks/flip_card.html'

    def get_context(self, value, parent_context=None):
        context = super().get_context(value, parent_context=parent_context)
        # context['is_happening_today'] = (value['date'] == datetime.date.today())
        # breakpoint()
        context['block_id'] = next(id_generator)
        # context['block_id'] = f"block_{self.id}"
        return context


class SingleLanguageCodeSnippetBlock(blocks.StructBlock):
    PYTHON = 'python'
    JAVA = 'java'
    JAVASCRIPT = 'js'
    BASH = 'bash'
    LANGUAGE_CHOICES = (
        (PYTHON,PYTHON),
        (JAVA,JAVA),
        (JAVASCRIPT,JAVASCRIPT),
        (BASH,BASH),
    )
    language = blocks.ChoiceBlock(choices = LANGUAGE_CHOICES)
    snippet  = blocks.TextBlock()

    content_panels = [
        FieldPanel('language'),
        FieldPanel('snippet'),
    ]

    # class Meta:
    #     template = 'home/blocks/single_language_code_snippet.html'




class MultiLanguageCodeSnippetBlock(blocks.StreamBlock):

    snippet = SingleLanguageCodeSnippetBlock()

    # content_panels = [
    #     ('snippet', FieldPanel('snippet'))
    # ]
    class Meta:
        template = 'home/blocks/multi_language_code_snippet.html'

    # def get_context(self, value, parent_context=None):
    #     context = super().get_context(value, parent_context=parent_context)
    #     # context['is_happening_today'] = (value['date'] == datetime.date.today())
    #     # breakpoint()
    #     # context['block_id'] = next(id_generator)
    #     # context['block_id'] = f"block_{self.id}"
    #     breakpoint()
        # return context
class ImageBlock(blocks.StructBlock):
    image = ImageChooserBlock()
    caption = blocks.RichTextBlock()

    class Meta:
        template = 'home/blocks/image.html'

class CurriculumContentItem(Page):

    prerequisites = models.ManyToManyField(
        "CurriculumContentItem",
        related_name="unlocks",
        through="ContentItemOrder",
        symmetrical=False,
    )

    body = StreamField([
        ('heading', HeadingBlock()),
        ('paragraph', blocks.RichTextBlock()),
        ('image', ImageBlock()),
        ('flip_card', FlipCardBlock()),
        ('code_snippet', MultiLanguageCodeSnippetBlock()),

    ])


    content_panels = Page.content_panels + [
        InlinePanel('pre_ordered_content', label="prerequisites",classname="collapsible collapsed"),
        InlinePanel('post_ordered_content', label="unlocks",classname="collapsible collapsed"),
        StreamFieldPanel('body', classname="full collapsible"),

    ]

    subpage_types=[]



# @register_snippet
# class BlogCategory(models.Model):
#     name = models.CharField(max_length=255)
#     icon = models.ForeignKey(
#         'wagtailimages.Image', null=True, blank=True,
#         on_delete=models.SET_NULL, related_name='+'
#     )

#     panels = [
#         FieldPanel('name'),
#         ImageChooserPanel('icon'),
#     ]

#     def __str__(self):
#         return self.name

#     class Meta:
#         verbose_name_plural = 'blog categories'
