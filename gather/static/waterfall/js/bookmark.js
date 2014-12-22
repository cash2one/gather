(function ($){
      $('#tiles').imagesLoaded(function() {
        // Prepare layout options.
        var options = {
          autoResize: true, // This will auto-update the layout when the browser window is resized.
          container: $('#main'), // Optional, used for some extra CSS styling
          offset: 2, // Optional, the distance between grid items
          itemWidth: 210, // Optional, the width of a grid item
          fillEmptySpace: true, // Optional, fill the bottom of each column with widths of flexible height
          ignoreInactiveItems: false,
          comparator: function(a, b) {
            return $(a).hasClass('inactive') && !$(b).hasClass('inactive') ? 1 : -1;
          }
        };

        // Get a reference to your grid items.
        var handler = $('#tiles li'),
            filters = $('#filters li');

        // Call the layout function.
        handler.wookmark(options);

        /**
         * When a filter is clicked, toggle it's active state and refresh.
         */
        var onClickFilter = function(event) {
          var item = $(event.currentTarget),
              activeFilters = [];
          item.toggleClass('active');

          // Collect active filter strings
          filters.filter('.active').each(function() {
            activeFilters.push($(this).data('filter'));
          });

          handler.wookmarkInstance.filter(activeFilters, 'or');
        }

        // Capture filter click events.
        filters.click(onClickFilter);
      });
    })(jQuery);