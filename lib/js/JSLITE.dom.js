/*
 * jsLite
 *
 * Copyright (c) 2009 - 2011 Benjamin Toll (benjamintoll.com)
 * Dual licensed under the MIT (MIT-LICENSE.txt)
 * and GPL (GPL-LICENSE.txt) licenses.
 *
 */

var $ = function (vElem, scope) {
  return typeof vElem === "string" ? (scope || document).getElementById(vElem) : vElem;
};

JSLITE.dom = (function () {

  var flyweight = {};

  return {
		
  /**
  * @function JSLITE.dom.attachHandler
  * @param {Array/String} vElem
  * @return {None}
  * @describe <p>Pass one or more methods (usually event handlers) as elements of an array, i.e., <code>["events.doThis", "global.doThat"]</code> or singularly as a <code>String</code>.</p><p>Must be objects of the <code>JSLITE</code> global symbol.</p>
  * @example
JSLITE.dom.attachHandler([
  "global.drawNavbarList",
  "events.addColumn",
  "events.moveDownColumn",
  "events.moveUpColumn",
  "events.subtractColumn",
  "superglobal.drawViewsList"
]);

JSLITE.ready(JSLITE.dom.attachHandler);
  */
  //<source>
  attachHandler: function (vElem) {
		
    /*
      - attach the handlers, argument can either be an array of
        strings or a single string;
      - each elem will be a namepaced string that's split by it's
        period, i.e. "events.slidingDoors" or "global.clickedFolder";
    */
    var aNamespace = [],
      i,
      len;

    if (vElem.constructor === Array) {
      for (i = 0, len = vElem.length; i < len; i++) {
        aNamespace = vElem[i].split(".");
        JSLITE[aNamespace[0]][aNamespace[1]](); //invoke the function;
      }
    } else { //it's just a string;
      aNamespace = vElem.split(".");
      JSLITE[aNamespace[0]][aNamespace[1]](); //invoke the function;
    }

  },
  //</source>
  
  /**
  * @function JSLITE.dom.blur
  * @param {Object} obj (Optional) Object literal, i.e., <code>{tag: "a", parent: "theDiv"}</code>
  * @return {None}
  * @describe <p>For Mozilla, blurs <code>links</code> (by default) and/or <code>inputs</code>.</p>
  */
  //<source>
  blur: function (obj) {

    if (obj && obj.tag !== "a" && obj.tag !== "input") {
      throw new Error("JSLITE.dom.blur(): This method only works on anchors and form inputs.");
    }

    var obj = obj || {}, //if no argument is passed set to an empty object;
      i,
      len,
      j,
      cElems = obj.parent ?
        $(obj.parent).getElementsByTagName(obj.tag || "a") :
          document.getElementsByTagName(obj.tag || "a");

    for (i = 0, len = cElems.length; i < len; i++) {
      if (cElems[i].type !== "text" && cElems[i].type !== "hidden") {
        cElems[i].onfocus = function () {
          if (this.blur) {
            this.blur();
          }
        };
      }
    }

    if (arguments.length > 1) { //allow for method overriding;
      for (j = 0; arguments[j] !== null; j++) {
        arguments.callee(arguments[j]);
      }
    }

  },
  //</source>

  /**
  * @function JSLITE.dom.cleanWhitespace
  * @param {String/HTMLElement} vElement
  * @return {None}
  * @describe <p>This method strips out all whitespace within the given <code>HTMLElement</code>.</p>
  */
  //<source>
  cleanWhitespace: function (vElement) {

    var element = (vElement && $(vElement)) || document,
      x,
      len,
      i,
      childNode;
		
    for (x = 0, len = element.childNodes.length; x < len; x++) {
      childNode = element.childNodes[x];
      if (childNode.nodeType === 3 && !/\S/.test(childNode.nodeValue)) {
        element.removeChild(element.childNodes[x]);
        x--;
      }
      if (childNode.nodeType === 1) {
        arguments.callee(childNode); //call this function;
      }
    }
    /*if more than one element is passed then call the function for
      each one (i.e., JSLITE.dom.cleanWhitespace("adminBar", "navbar"));
    */
    if (arguments.length > 1) {
      for (i = 1; arguments[i] !== null; i++) {
        arguments.callee(arguments[i]);
      }
    }

  },
  //</source>

  event: (function () {
		
    var _find = function (element, eventType, handler) {
      var handlers = element._handlers;
      if (!handlers) {
        return -1;
      }
		
      var d = element.document || element;
      var w = d.parentWindow;
		
      for (var i = handlers.length; i >= 0; i--) {
        var handlerId = handlers[i];
        var h = w._allHandlers[handlerId];
			
        if (h && h.eventType === eventType && h.handler === handler) {
          return i;
        }
      }
		
      return -1
    };
	
    var _removeAllHandlers = function () {
      var w = this;
      for (var id in w._allHandlers) {
        if (w._allHandlers.hasOwnProperty(id)) {
          var h = w._allHandlers[id];
          h.element.detachEvent("on" + h.eventType, h.wrappedHandler);
          delete w._allHandlers[id];
        }
      }
    };

    var _uid = (function () {
      var _counter = 0;
      return function () { return "h" + _counter++; };
    }());
	
    return {
		
      add: function (element, eventType, handler) {
        if (document.addEventListener) {
          element.addEventListener(eventType, handler, false);
				
        } else if (document.attachEvent) {

          if (_find(element, eventType, handler) !== -1) return;
		
          var wrappedHandler = function (e) {
            if (!e) e = window.event;
			
            var event = {
              _event: e,
              type: e.type,
              target: e.srcElement,
              currentTarget: element,
              relatedTarget: e.fromElement ? e.fromElement : e.toElement,
              eventPhase: (e.srcElement === element) ? 2 : 3,
				
              clientX: e.clientX, clientY: e.clientY,
              screenX: e.screenX, screenY: e.screenY,
				
              altKey: e.altKey, ctrlKey: e.ctrlKey,
              shiftKey: e.shiftKey, charCode: e.charCode,
              keyCode: e.keyCode,
				
              stopPropagation: function () { this._event.cancelBubble = true; },
              preventDefault: function () { this._event.returnValue = false; }
            };
			
            if (Function.prototype.call) {
              handler.call(element, event);
            } else {
              element._currentHandler = handler;
              element._currentHandler(event);
              element._currentHandler = null;
            }
          };
		
          element.attachEvent("on" + eventType, wrappedHandler);
		
          var h = {
            element: element,
            eventType: eventType,
            handler: handler,
            wrappedHandler: wrappedHandler
          };
		
          var d = element.document || element;
          var w = d.parentWindow;
		
          var id = _uid();
          if (!w._allHandlers) w._allHandlers = {};
          w._allHandlers[id] = h;
		
          if (!element._handlers) element._handlers = [];
          element._handlers.push(id);
		
          if (!w._onunloadHandlerRegistered) {
            w._onunloadHandlerRegistered = true;
            w.attachEvent("onunload", _removeAllHandlers);
          }
		
        }
      },

      remove: function (element, eventType, handler) {
        if (document.removeEventListener) {
          element.removeEventListener(eventType, handler, false);
				
        } else if (document.detachEvent) {
				
          var i = _find(element, eventType, handler);
          if (i === -1) {
            return;
          }
		
          var d = element.document || element;
          var w = d.parentWindow;
		
          var handlerId = element._handlers[i];
          var h = w._allHandlers[handlerId];
		
          element.detachEvent("on" + eventType, h.wrappedHandler);
          element._handlers.splice(i, 1);
          delete w._allHandlers[handlerId];
		
        }
      }
      //</source>
		
    }; //end return object;
	
  }()),

  /**
  * @function JSLITE.dom.find
  * @param {String/HTMLElement/JSLITE.Element} vElem
  * @param {String} sSelector
  * @return {HTMLElement/Boolean}
  * @describe <p>This method finds an ancestor element of <code>vElem</code> by interrogating each of its parent elements using the passed selector. Uses <code><a href="#jsdoc">JSLITE.domQuery</a></code> internally.</p><p>Returns either the found dom element or <code>false</code>.</p>
  * @example
JSLITE.dom.find("test", "#box3[style$=100px;]");
  */
  //<source>
  find: function (vElem, sSelector) {

    if (!vElem || !sSelector) {
      throw new Error("Failure to provide arguments in method JSLITE.dom.find");
    }

    var oElem = JSLITE.Element.get(vElem, true).parentNode;
    while (oElem) {
      if (JSLITE.domQuery.find(oElem, sSelector)) {
        return oElem;
      }
      oElem = oElem.parentNode;
    }
    return false;

  },
  //</source>

  /**
  * @function JSLITE.dom.id
  * @param {None}
  * @return {Number}
  * @describe <p>Gives an <code>HTMLElement</code> a unique ID if it doesn't already have one. Inspired by ExtJS</p>
  */
  //<source>
  id: function () {

    return JSLITE.globalSymbol + JSLITE.counter();

  },
  //</source>

  /**
  * @function JSLITE.dom.insertAfter
  * @param {HTMLElement} newElement
  * @param {HTMLElement} targetElement
  * @return {None}
  * @describe <p>Inserts <code>newElement</code> after <code>targetElement</code> in the DOM.</p>
<p>Use this helper method when not wanting to instantiate a <code><a href="#jsdoc">JSLITE.Element</a></code> and thereby invoking <code><a href="#jsdoc">JSLITE.Element.after</a></code>.</p>
  */
  //<source>
  insertAfter: function (newElement, targetElement) {

    var parent = targetElement.parentNode;
    if (parent.lastChild === targetElement) {
      parent.appendChild(newElement);
    } else {
      parent.insertBefore(newElement, targetElement.nextSibling);
    }

  },
  //</source>

  /**
  * @function JSLITE.dom.insertHtml
  * @param {String} sWhere Where to insert the html in relation to <code>oElem</code> - beforeBegin, afterBegin, beforeEnd, afterEnd.
  * @param {HTMLElement} oElem
  * @param {String} sHtml
  * @return {HTMLElement}
  * @describe <p>Easily allows for inserting HTML in the document tree.</p>
  * @example
Example:

<ul>
  <li>one</li>
  <li>two</li>
  <li>three</li>
  <li>four</li>
  <li>five</li>
</ul>

What if you need to append text to one of the list items?  innerHTML kills an element's
children, and performing an operation to first retrieve the child node and then append
the new text isn't convenient.

var sHtml = " <strong>hundred</strong>";
JSLITE.dom.insertHtml("beforeEnd", document.getElementsByTagName("li")[1], sHtml);

So the list becomes:

<ul>
  <li>one</li>
  <li>two <strong>hundred</strong></li>
  <li>three</li>
  <li>four</li>
  <li>five</li>
</ul>

This is a simple example but the concept can easily be grasped.
  */
  //<source>
  insertHtml: function (sWhere, oElem, sHtml){

    sWhere = sWhere.toLocaleLowerCase();
    if (oElem.insertAdjacentHTML) {

      switch (sWhere) {
        case "beforebegin":
          oElem.insertAdjacentHTML("BeforeBegin", sHtml);
          return oElem.previousSibling;

        case "afterbegin":
          oElem.insertAdjacentHTML("AfterBegin", sHtml);
          return oElem.firstChild;

        case "beforeend":
          oElem.insertAdjacentHTML("BeforeEnd", sHtml);
          return oElem.lastChild;

        case "afterend":
          oElem.insertAdjacentHTML("AfterEnd", sHtml);
          return oElem.nextSibling;

      }
      throw 'Illegal insertion point -> "' + sWhere + '"';
    }

    var range = oElem.ownerDocument.createRange(),
      frag;

    switch (sWhere) {
      case "beforebegin":
        range.setStartBefore(oElem);
        frag = range.createContextualFragment(sHtml);
        oElem.parentNode.insertBefore(frag, oElem);
        return oElem.previousSibling;

      case "afterbegin":
        if (oElem.firstChild) {
          range.setStartBefore(oElem.firstChild);
          frag = range.createContextualFragment(sHtml);
          oElem.insertBefore(frag, oElem.firstChild);
          return oElem.firstChild;

        } else {
          oElem.innerHTML = sHtml;
          return oElem.firstChild;
        }

      case "beforeend":
        if (oElem.lastChild) {
          range.setStartAfter(oElem.lastChild);
          frag = range.createContextualFragment(sHtml);
          oElem.appendChild(frag);
          return oElem.lastChild;

        } else {
          oElem.innerHTML = sHtml;
          return oElem.lastChild;
        }

      case "afterend":
        range.setStartAfter(oElem);
        frag = range.createContextualFragment(sHtml);
        oElem.parentNode.insertBefore(frag, oElem.nextSibling);
        return oElem.nextSibling;
    }
    throw 'Illegal insertion point -> "' + sWhere + '"';

  },
  //</source>

  /**
  * @function JSLITE.dom.isTextBox
  * @param {HTMLElement/JSLITE.Element} oElem
  * @return {Boolean}
  * @describe <p>A handy way to quickly determine if an element is a textbox or a textarea.  Useful for string trimming and validation.</p>
  * @example
var oDom = JSLITE.Element.get(this, true);
if (!JSLITE.dom.isTextBox(oDom)) return;
oDom.value = JSLITE.trim(oDom.value);
return this;
  */
  //<source>
  isTextBox: function (oElem) {

    oElem = JSLITE.Element.get(oElem, true);
    return oElem.nodeName.toLocaleLowerCase() === "input" &&
      oElem.type === "text" ||
        oElem.nodeName.toLocaleLowerCase() === "textarea";

  },
  //</source>

  /**
  * @function JSLITE.dom.remove
  * @param {String/Array} vToRemove Can be either a single HTMLElement to remove or an Array of HTMLElements
  * @return {HTMLElement/Array} - One or more <code>HTMLElements</code>
  * @describe <p>Removes one or more <code>HTMLElements</code> from the DOM and returns the removed element(s).</p>
<p>Use this helper method when not wanting to instantiate a <code><a href="#jsdoc">JSLITE.Element</a></code> and thereby invoking <code><a href="#jsdoc">JSLITE.Element.remove</a></code>.</p>
  * @example
var oElems = JSLITE.dom.remove("test");

var aElems = JSLITE.dom.remove(["test", "anotherTest", "oneMore"]);
  */
  //<source>
  remove: function (vToRemove) {

    var vRemovedElements,
      oElem,
      i,
      len;
    
    if (!vToRemove) {
      return false;
    }

    if (typeof vToRemove === "string") {
      oElem = $(vToRemove);
      if (oElem) {
        return oElem.parentNode.removeChild(oElem);
      }
		
    } else if (vToRemove.constructor === Array) {
      vRemovedElements = [];
      for (i = 0, len = vToRemove.length; i < len; i++) {
        oElem = $(vToRemove[i]);
        if (oElem) {
          vRemovedElements.push(oElem.parentNode.removeChild(oElem));
        }
      }
      return vRemovedElements;
    }

  },
  //</source>
	
  //<source>
  removeChildren: function (kids) {

    /*kids can either be an array (remove multiple nodes at once) or an object or a string (only remove one node)*/
    if (kids.constructor === Array) {
      for (var i = 0, len = kids.length; i < len; i++) {
        $(kids[i]).parentNode.removeChild(elem);
      }
    } else {
      $(kids).parentNode.removeChild(elem);
    }

  },
  //</source>
	
  /**
  * @function JSLITE.dom.targetBlank
  * @param {None}
  * @return {Boolean}
  * @describe <p>Mimics the behavior of the deprecated <code>target="_blank"</code>. Assumes that the link that launches a browser to be opened in a new window has a <code>rel</code> attribute set to <code>external</code> or <code>pdf</code>.</p>
  */
  //<source>
  targetBlank: function () {

    var cLinks = document.getElementsByTagName("a"),
      i,
      len,
      child;

    for (i = 0, len = cLinks.length; i < len; i++) {
      if (cLinks[i].getAttribute("rel") &&
        cLinks[i].getAttribute("rel") === "external" ||
          cLinks[i].getAttribute("rel") === "pdf") {

        cLinks[i].onclick = function() {
          child = window.open(this.getAttribute('href'));
          return !child ? true /*failed to open so follow link*/:
            false; /*success, open new browser window*/
        };

      }
    }

  }
  //</source>

  }; //end returned object;

}());
