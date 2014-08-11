if Backbone?
  class @DiscussionContentView extends Backbone.View


    events:
      "click .discussion-flag-abuse": "toggleFlagAbuse"
      "keydown .discussion-flag-abuse":
        (event) -> DiscussionUtil.activateOnSpace(event, @toggleFlagAbuse)

    attrRenderer:
      ability: (ability) ->
        for action, selector of @abilityRenderer
          if not ability[action]
            selector.disable.apply(@)
          else
            selector.enable.apply(@)

    abilityRenderer:
      editable:
        enable: -> @$(".action-edit").closest("li").show()
        disable: -> @$(".action-edit").closest("li").hide()
      can_delete:
        enable: -> @$(".action-delete").closest("li").show()
        disable: -> @$(".action-delete").closest("li").hide()

      can_openclose:
        enable: -> @$(".action-close").closest("li").show()
        disable: -> @$(".action-close").closest("li").hide()

    renderPartialAttrs: ->
      for attr, value of @model.changedAttributes()
        if @attrRenderer[attr]
          @attrRenderer[attr].apply(@, [value])

    renderAttrs: ->
      for attr, value of @model.attributes
        if @attrRenderer[attr]
          @attrRenderer[attr].apply(@, [value])

    makeWmdEditor: (cls_identifier) =>
      if not @$el.find(".wmd-panel").length
        DiscussionUtil.makeWmdEditor @$el, $.proxy(@$, @), cls_identifier

    getWmdEditor: (cls_identifier) =>
      DiscussionUtil.getWmdEditor @$el, $.proxy(@$, @), cls_identifier

    getWmdContent: (cls_identifier) =>
      DiscussionUtil.getWmdContent @$el, $.proxy(@$, @), cls_identifier

    setWmdContent: (cls_identifier, text) =>
      DiscussionUtil.setWmdContent @$el, $.proxy(@$, @), cls_identifier, text


    initialize: ->
      @model.bind('change', @renderPartialAttrs, @)

  class @DiscussionContentShowView extends DiscussionContentView
    events:
      "click .action-follow": "toggleFollow"
      "click .action-answer": "toggleEndorse"
      "click .action-endorse": "toggleEndorse"
      "click .action-vote": "toggleVote"
      "click .action-pin": "togglePin"
      "click .action-edit": "edit"
      "click .action-delete": "_delete"
      "click .action-report": "toggleReport"
      "click .action-close": "toggleClose"

    updateButtonState: (selector, checked) =>
      $button = @$(selector)
      $button.toggleClass("is-checked", checked)
      $button.attr("aria-checked", checked)

    attrRenderer:
      subscribed: (subscribed) ->
        @updateButtonState(".action-follow", subscribed)

      endorsed: (endorsed) ->
        selector = if @model.get("thread").get("thread_type") == "question" then ".action-answer" else ".action-endorse"
        @updateButtonState(selector, endorsed)
        $button = @$(selector)
        $button.toggleClass("is-clickable", @model.canBeEndorsed())
        $button.toggleClass("is-checked", endorsed)
        if endorsed || @model.canBeEndorsed()
          $button.removeAttr("hidden")
        else
          $button.attr("hidden", "hidden")

      votes: (votes) ->
        selector = ".action-vote"
        @updateButtonState(selector, window.user.voted(@model))
        button = @$el.find(selector)
        numVotes = votes.up_count
        button.find(".js-sr-vote-count").html(
          interpolate(gettext("currently %(numVotes)s votes"), {numVotes: numVotes}, true)
        )
        button.find(".js-visual-vote-count").html("" + numVotes)

      pinned: (pinned) ->
        @updateButtonState(".action-pin", pinned)

      abuse_flaggers: (abuse_flaggers) ->
        flagged = (
          window.user.id in abuse_flaggers or
          (DiscussionUtil.isFlagModerator and abuse_flaggers.length > 0)
        )
        @updateButtonState(".action-report", flagged)

      closed: (closed) ->
        @updateButtonState(".action-close", closed)
        @$(".post-status-closed").toggle(closed)

    toggleFollow: (event) =>
      event.preventDefault()
      is_subscribed = @model.get("subscribed")
      url = @model.urlFor(if is_subscribed then "unfollow" else "follow")
      DiscussionUtil.updateWithUndo(
        @model,
        {"subscribed": not is_subscribed},
        {url: url, type: "POST", $elem: $(event.currentTarget)}
      )

    toggleEndorse: (event) =>
      event.preventDefault()
      if not @model.canBeEndorsed()
        return
      is_endorsed = @model.get("endorsed")
      url = @model.urlFor("endorse")
      updates =
        endorsed: not is_endorsed
        endorsement: if is_endorsed then null else {username: DiscussionUtil.getUser().get("username"), time: new Date().toISOString()}
      DiscussionUtil.updateWithUndo(
        @model,
        updates,
        {url: url, type: "POST", data: {endorsed: not is_endorsed}, $elem: $(event.currentTarget)},
      ).done(() => @trigger "comment:endorse", not is_endorsed)

    toggleVote: (event) =>
      event.preventDefault()
      user = DiscussionUtil.getUser()
      did_vote = user.voted(@model)
      url = @model.urlFor(if did_vote then "unvote" else "upvote")
      updates =
        upvoted_ids: (if did_vote then _.difference else _.union)(user.get('upvoted_ids'), [@model.id])
      DiscussionUtil.updateWithUndo(
        user,
        updates,
        {url: url, type: "POST", $elem: $(event.currentTarget)},
      ).done(() => if did_vote then @model.unvote() else @model.vote())

    togglePin: (event) =>
      event.preventDefault()
      is_pinned = @model.get("pinned")
      url = @model.urlFor(if is_pinned then "unPinThread" else "pinThread")
      errorFunc = () =>
        if newPinned
          msg = gettext("We had some trouble pinning this thread. Please try again.")
        else
          msg = gettext("We had some trouble unpinning this thread. Please try again.")
        DiscussionUtil.discussionAlert(gettext("Sorry"), msg)
      DiscussionUtil.updateWithUndo(
        @model,
        {pinned: not is_pinned},
        {url: url, type: "POST", error: errorFunc, $elem: $(event.currentTarget)},
      )

    toggleReport: (event) =>
      event.preventDefault()
      user = DiscussionUtil.getUser()
      if user.id in @model.get("abuse_flaggers") or (DiscussionUtil.isFlagModerator and @model.get("abuse_flaggers").length > 0)
        is_flagged = true
      else
        is_flagged = false
      url = @model.urlFor(if is_flagged then "unFlagAbuse" else "flagAbuse")
      updates =
        abuse_flaggers: (if is_flagged then _.difference else _.union)(@model.get("abuse_flaggers"), [user.id])
      DiscussionUtil.updateWithUndo(
        @model,
        updates,
        {url: url, type: "POST", $elem: $(event.currentTarget)},
      )

    toggleClose: (event) =>
      event.preventDefault()
      DiscussionUtil.updateWithUndo(
        @model,
        {closed: not @model.get('closed')},
        {url: @model.urlFor("close"), type: "POST", $elem: $(event.currentTarget)},
      )
