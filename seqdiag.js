// Globals

let theSourceDoc = { dom: '', fileName: 'untitled.uml', isModified: false };

let xslSVG;

fetch('./svg.xsl')
  .then(response => {
    if (response.ok) {
      return response.text()
    } else {
      return Promise.reject('error: ' + response.status)
    }
  })
  .then(data => {
    const parser = new DOMParser();
    // assign to the global variable xslSVG above
    xslSVG = parser.parseFromString(data, 'application/xml');
    //console.log(xslSVG);
    loadEmptyDocument();
  })
  .catch(error => console.error(error));

// Functions
function loadEmptyDocument() {
    // initial empty doc
    const theEmptyTxt = `<?xml version="1.0"?>
<sequencediagml>
    <parameters>
        <hspacing>240</hspacing>
        <vspacing>20</vspacing>
        <max_t>30</max_t>
        <fontsize>12</fontsize>
    </parameters>
    <lifelinelist/>
    <messagelist/>
    <framelist/>
</sequencediagml>`;
    const parser = new DOMParser();
    theSourceDoc.dom = parser.parseFromString(theEmptyTxt, "application/xml");
    const xsltProcessor = new XSLTProcessor();
    xsltProcessor.importStylesheet(xslSVG);
    const theSvgDoc = xsltProcessor.transformToDocument(theSourceDoc.dom);
    const theSvgParent=document.getElementById('svg_parent');
    theSvgParent.innerHTML = '';
    theSvgParent.appendChild(theSvgDoc.documentElement);
}

function loadFileDocument() {
    const fileList = this.files;
    const file = fileList[0];
    //console.log(file.name);
    const reader = new FileReader();
    reader.onload = function(event) {
        const contents = event.target.result;
        const parser = new DOMParser();
        theSourceDoc.dom = parser.parseFromString(contents, "application/xml");
        theSourceDoc.isModified = false;
        theSourceDoc.fileName = file.name;
        closeDialogs();
        populateUi();
    };
    reader.readAsText(file);
}

function loadExampleDocument() {
    // a fixed hard-coded example doc
    const theExampleTxt = `<?xml version="1.0" encoding="UTF-8"?>
<sequencediagml>
    <parameters>
        <hspacing>240</hspacing>
        <vspacing>26</vspacing>
        <max_t>20</max_t>
        <fontsize>12</fontsize>
    </parameters>
    <lifelinelist>
        <lifeline type="actor">
            <lifelinename>random guy</lifelinename>
            <activitybars>
                <activitybar begin_t="1" end_t="20"/>
            </activitybars>
        </lifeline>
        <lifeline type="object">
            <lifelinename>an object</lifelinename>
            <activitybars>
                <activitybar begin_t="1" end_t="20"/>
            </activitybars>
        </lifeline>
        <lifeline type="object">
            <lifelinename>another object</lifelinename>
            <activitybars>
                <activitybar begin_t="12" end_t="13"/>
            </activitybars>
        </lifeline>
        <lifeline type="object" destroy_t="18">
            <lifelinename>an ephemeral object</lifelinename>
            <activitybars>
                <activitybar begin_t="8" end_t="12"/>
                <activitybar begin_t="16" end_t="17"/>
            </activitybars>
        </lifeline>
        <lifeline type="object">
            <lifelinename>yet another object</lifelinename>
            <activitybars>
                <activitybar begin_t="1" end_t="20"/>
            </activitybars>
        </lifeline>
    </lifelinelist>
    <messagelist>
        <message type="asynchronous" from="0" to="1" t="2">
            <messagetext>begin</messagetext>
        </message>
        <message type="create" from="1" to="3" t="3">
            <messagetext>create object</messagetext>
        </message>
        <message type="reflexive" from="1" t="7">
            <messagetext>reflexive message</messagetext>
        </message>
        <message type="synchronous" from="4" to="3" t="8">
            <messagetext>synchronous message</messagetext>
            <response t="12">response</response>
        </message>
        <message type="asynchronous" from="1" to="2" t="12">
            <messagetext>asynchronous message</messagetext>
        </message>
        <message type="asynchronous" from="1" to="3" t="16">
            <messagetext>destroy object</messagetext>
        </message>
    </messagelist>
    <framelist>
        <frame type="SD" widthfactor="1">Example Diagram</frame>
        <frame type="ALT" left="1" right="2" top="5" bottom="14" alttext="[else]" altt="10">[condition x]</frame>
    </framelist>
</sequencediagml>`;
    const parser = new DOMParser();
    theSourceDoc.dom = parser.parseFromString(theExampleTxt, "application/xml");
    theSourceDoc.isModified = false;
    theSourceDoc.fileName = 'example.uml';
    closeDialogs();
    populateUi();
}

function closeDialogs() {
  hideFrameDialog();
  hideMessageDialog();
  hideLifelineDialog();
  hideLayoutDialog();
}

function getMaxT() {
  return theSourceDoc.dom.getElementsByTagName('max_t')[0].textContent;
}

function tAxisShow(event) {
  const btn = event.target;
  if (btn.textContent == 'Show t Axis') {
    btn.textContent = 'Hide t Axis';
  } else {
    btn.textContent = 'Show t Axis'
  }
  populateUi();
}

function updateScale(event) {
  document.getElementById('scaleValue').innerText = (event.target.value * 100) + '%';
  populateUi();
}

function populateUi() {
    // theSourceDoc.dom and xslSVG are application globals
    const xsltProcessor = new XSLTProcessor();
    xsltProcessor.importStylesheet(xslSVG);
    const scaleFactor = document.getElementById('scaling').value;
    xsltProcessor.setParameter(null, 'SCALEFACTOR', scaleFactor);
    if (document.getElementById('toggleScaleButton').textContent == 'Hide t Axis') {
      xsltProcessor.setParameter(null, 'SHOWSCALE', 'yes');
    }
    const theSvgDoc = xsltProcessor.transformToDocument(theSourceDoc.dom);
    const theSvgParent=document.getElementById('svg_parent');
    theSvgParent.innerHTML = '';
    theSvgParent.appendChild(theSvgDoc.documentElement);

    // re-apply any highlighted svg elements
    const lifelineIndex = document.getElementById('lifelineIdx');
    if (document.getElementById('lifelineDialog').style.visibility == 'visible') {
      const lifelineSvg = document.getElementById('lifeline_' + lifelineIndex.value);
      if (lifelineSvg != null) {
        lifelineSvg.setAttributeNS(null, 'filter', 'url(#dropshadow)');
      }
    }
    const messageIndex = document.getElementById('messageIdx')
    if (document.getElementById('messageDialog').style.visibility == 'visible') {
      const messageSvg = document.getElementById('message_' + messageIndex.value);
      if (messageSvg != null) {
        messageSvg.setAttributeNS(null, 'filter', 'url(#dropshadow)');
      }
    }
    const frameIndex = document.getElementById('frameIdx')
    if (document.getElementById('frameDialog').style.visibility == 'visible') {
      const frameSvg = document.getElementById('frame_' + frameIndex.value);
      if (frameSvg != null) {
        frameSvg.setAttributeNS(null, 'filter', 'url(#dropshadow)');
      }
    }

    populateLayoutDialog();

    const theLifelineList = document.getElementById('lifelines');
    // clear existing lifelines from select before re-populating
    const existingLifelines = document.getElementById('existingLifelineGroup');
    if (existingLifelines != null) {
      theLifelineList.removeChild(existingLifelines);
    }
    const optLifelineGroup = document.createElement('optgroup');
    optLifelineGroup.setAttribute('label', 'Edit or Delete');
    optLifelineGroup.setAttribute('id', 'existingLifelineGroup');

    // clear lifeline lists from message dialog
    const fromList = document.getElementById('fromLifeline');
    const fromSelectedOld = fromList.selectedIndex;
    fromList.innerHTML = '';
    const toList = document.getElementById('toLifeline');
    const toSelectedOld = toList.selectedIndex;
    toList.innerHTML = '';
    // clear from frame dialog
    const leftList = document.getElementById('leftLifeline');
    const leftSelectedOld = leftList.selectedIndex;
    leftList.innerHTML = '';
    const rightList = document.getElementById('rightLifeline');
    const rightSelectedOld = rightList.selectedIndex;
    rightList.innerHTML = '';

    const lifelineNodes = theSourceDoc.dom.getElementsByTagName("lifeline");
    if (lifelineNodes.length) {
      for (i = 0; i <lifelineNodes.length; i++) {
        const option = document.createElement("option");
        option.innerHTML = (i + 1).toString() + ". " + (lifelineNodes[i].getElementsByTagName("lifelinename")[0].textContent).substring(0, 15);
        option.value = i;
        optLifelineGroup.appendChild(option);
        // populate message dialog "from" and "to" lists
        fromList.appendChild(option.cloneNode(true));
        toList.appendChild(option.cloneNode(true));
        // populate frame dialog
        leftList.appendChild(option.cloneNode(true));
        rightList.appendChild(option.cloneNode(true));
        // add click handler to svg lifeline
        const lifelineSvg = document.getElementById('lifeline_' + i);
        lifelineSvg.addEventListener('click', showLifelineDialogSvg);
      }
      theLifelineList.appendChild(optLifelineGroup);
      theLifelineList.size = lifelineNodes.length + 3;
      fromList.selectedIndex = fromSelectedOld;
      toList.selectedIndex = toSelectedOld;
      leftList.selectedIndex = leftSelectedOld;
      rightList.selectedIndex = rightSelectedOld;
    }

    const theMessageList = document.getElementById('messages');
    // clear existing messages from select before re-populating
    const existingMessages = document.getElementById('existingMessageGroup');
    if (existingMessages != null) {
      theMessageList.removeChild(existingMessages);
    }
    const optMessageGroup = document.createElement('optgroup');
    optMessageGroup.setAttribute('label', 'Edit or Delete');
    optMessageGroup.setAttribute('id', 'existingMessageGroup');
    const messageNodes = theSourceDoc.dom.getElementsByTagName("message");
    if (messageNodes.length) {
      for (i = 0; i < messageNodes.length; i++) {
        const option = document.createElement("option");
        option.innerHTML = (i + 1).toString() + ". " + messageNodes[i].getElementsByTagName("messagetext")[0].textContent;
        option.value = i;
        optMessageGroup.appendChild(option);
        const messageSvg = document.getElementById('message_' + i);
        messageSvg.addEventListener('click', showMessageDialogSvg);
      }
      theMessageList.appendChild(optMessageGroup);
      theMessageList.size = messageNodes.length + 3;
    }

    const theFrameList = document.getElementById('frames');
    // clear existing frames from select before re-populating
    const existingFrames = document.getElementById('existingFrameGroup');
    if (existingFrames != null) {
      theFrameList.removeChild(existingFrames);
    }
    const optFrameGroup = document.createElement('optgroup');
    optFrameGroup.setAttribute('label', 'Edit or Delete');
    optFrameGroup.setAttribute('id', 'existingFrameGroup');
    const frameNodes = theSourceDoc.dom.getElementsByTagName("frame");
    if (frameNodes.length) {
      for (i = 0; i < frameNodes.length; i++) {
        const option = document.createElement("option");
        option.innerHTML = (i + 1).toString() + ". " + frameNodes[i].getAttribute('type') + ' ' + frameNodes[i].textContent;
        option.value = i;
        optFrameGroup.appendChild(option);
        const frameSvg = document.getElementById('frame_' + i);
        frameSvg.addEventListener('click', showFrameDialogSvg);
      }
      theFrameList.appendChild(optFrameGroup);
      theFrameList.size = frameNodes.length + 3;
    }

    const fileBanner = document.getElementById('file_banner');
    fileBanner.innerText = theSourceDoc.fileName;
    if (theSourceDoc.isModified) {
      fileBanner.innerText += '*';
    }
}

function saveUmlDocument() {
    if (theSourceDoc.dom != null) {
      const filename = prompt('File will be saved in your browser Download directory.\nFile will be saved as: ', theSourceDoc.fileName);
      if (filename) {
        if (filename != theSourceDoc.fileName) {
          theSourceDoc.fileName = filename;
        }
        const s = new XMLSerializer();
        let content = s.serializeToString(theSourceDoc.dom);
        content = content.replace(/>\s*/g, '>');
        content = content.replace(/\s*</g, '<');
        //console.log(content);
        saveDocument(content, theSourceDoc.fileName);
        theSourceDoc.isModified = false;
        const fileBanner = document.getElementById('file_banner');
        fileBanner.innerText = theSourceDoc.fileName;
      }
    }
}

function saveSvgDocument() {
    if (theSourceDoc.dom != null) {
      const svgFilename = prompt('File will be saved in your browser Download directory.\nFile will be saved as: ', theSourceDoc.fileName.replace(/\..*/g, '.svg'))
      if (svgFilename) {
        const xsltProcessor = new XSLTProcessor();
        xsltProcessor.importStylesheet(xslSVG);
        xsltProcessor.setParameter(null, 'BOUNDINGRECTS', 'no');
        const theSvgDoc = xsltProcessor.transformToDocument(theSourceDoc.dom);
        const s = new XMLSerializer();
        const contentSvg = s.serializeToString(theSvgDoc);
        saveDocument(contentSvg, svgFilename);
      }
    }
}

function saveDocument(content, fileName2Use) {
    // Create element with <a> tag
    const link = document.createElement("a");
    // Create a blob object with the file content which you want to add to the file
    const file = new Blob([content], { type: 'text/plain' });
    // Add file content in the object URL
    link.href = URL.createObjectURL(file);
    // Add file name
    link.download = fileName2Use;
    // Add click event to <a> tag to save file.
    link.click();
    URL.revokeObjectURL(link.href);
}
///////////////////////////
function showLifelineDialogSvg(event) {
  const lifelineIndex = event.target.parentElement.id.split('_')[1];
  showLifelineDialog(lifelineIndex);
}

function showLifelineDialogSelect(event) {
  showLifelineDialog(event.target.value);
}

function showLifelineDialog(lifelineIndex) {
  hideLifelineDialog();
  const maxT = getMaxT();
  document.getElementById('destroyT').setAttribute('max', maxT - 1);
  document.getElementById('bbar').setAttribute('max', maxT - 1);
  document.getElementById('ebar').setAttribute('max', maxT);
  if (isNaN(parseInt(lifelineIndex))) {
    resetLifelineDialog();
  } else {
    populateLifelineDialog(lifelineIndex);
    const lifelineSvg = document.getElementById('lifeline_' + lifelineIndex);
    lifelineSvg.setAttributeNS(null, 'filter', 'url(#dropshadow)');
  }
  document.getElementById('lifelineDialog').style.visibility = 'visible';
}

function resetLifelineDialog() {
  document.getElementById('lifelineDialogHeader').textContent = 'New Lifeline';
  document.getElementById('lifelineIdx').value = 'new';
  document.getElementById('lifelineType').selectedIndex = -1;
  document.getElementById('lifelineName').value = '';
  const barList = document.querySelectorAll('.barRow');
  for (i = 0; i < barList.length; i++) {
    barList[i].remove();
  }
  document.getElementById('showNewActBar').checked = false;
  document.getElementById('newActBar').style.display = 'none';
  document.getElementById('ebar').value = '';
  document.getElementById('bbar').value = '';
  document.getElementById('showFiniteLifeline').checked = false;
  document.getElementById('finiteLifeline').style.display = 'none';
  document.getElementById('destroyT').value = '';
  document.getElementById('deleteLifelineDialogBtn').setAttribute('hidden', 'hidden');
  disableApplyLifelineDialog();
}

function populateLifelineDialog(lifelineIdx) {
  document.getElementById('lifelineDialogHeader').textContent = 'Edit Lifeline'
  const lifelineData = theSourceDoc.dom.getElementsByTagName("lifeline")[lifelineIdx];
//  const s = new XMLSerializer();
//  const content = s.serializeToString(lifelineData);
//  console.log(content);
  document.getElementById('lifelineIdx').value = lifelineIdx;
  document.getElementById('lifelineName').value = lifelineData.getElementsByTagName('lifelinename')[0].textContent;
  document.getElementById('lifelineType').value = lifelineData.getAttribute('type');
  const barData = lifelineData.getElementsByTagName('activitybars')[0].getElementsByTagName('activitybar');

  resetActivityBars(barData);

  if (lifelineData.getAttribute('destroy_t')) {
    document.getElementById('showFiniteLifeline').checked = true;
    document.getElementById('finiteLifeline').style.display = 'inline-block';
    document.getElementById('destroyT').value = lifelineData.getAttribute('destroy_t');
  } else {
    document.getElementById('showFiniteLifeline').checked = false;
    document.getElementById('finiteLifeline').style.display = 'none';
    document.getElementById('destroyT').value = '';
  }
  document.getElementById('deleteLifelineDialogBtn').removeAttribute('hidden');
  disableApplyLifelineDialog();
}

function resetActivityBars(barData) {
  const barList = document.querySelectorAll('.barRow');
  for (i = 0; i < barList.length; i++) {
    barList[i].remove();
  }
  const actBarTableBody =  document.getElementById('activityBarsRows');
  if (barData.length) {
    document.getElementById('existingActBars').style.display = 'inline-block';
    for (i = 0; i < barData.length; i++) {
      const barRowId = 'barRow_' + i;
      const delBtnId = 'delBtnRow_' + i;;
      actBarTableBody.insertAdjacentHTML('beforeend', '<tr id="' + barRowId +'" class="barRow"><td>' + barData[i].getAttribute('begin_t') + '</td><td>' + barData[i].getAttribute('end_t') + '</td><td><button id ="'+ delBtnId + '" class="delBar" value="' + i + '">-&nbsp;</button></td></tr>');
      document.getElementById(delBtnId).addEventListener("click", removeActivityBar, false);
    }
  } else {
    document.getElementById('existingActBars').style.display = 'none';
  }
  document.getElementById('showNewActBar').checked = false;
  document.getElementById('newActBar').style.display = 'none';
  document.getElementById('bbar').value = '';
  document.getElementById('ebar').value = '';
}

function hideLifelineDialog() {
  document.getElementById('lifelineDialog').style.visibility = 'hidden';
  const lifelineIndex = document.getElementById('lifelineIdx');
  const lifelineSvg = document.getElementById('lifeline_' + lifelineIndex.value);
  if (lifelineSvg != null) {
    lifelineSvg.removeAttribute('filter');
  }
}

function enableApplyLifelineDialog() {
  // could do cross-field validations here
  if (document.getElementById('lifelineType').selectedIndex == '-1') {
    alert('please select a lifeline type');
  } else {
    document.getElementById('applyLifelineDialogBtn').disabled = false;
  }
}

function disableApplyLifelineDialog() {
  document.getElementById('applyLifelineDialogBtn').disabled = true;
}

function showMessageDialogSvg (event) {
  const messageIndex = event.target.parentElement.id.split('_')[1];
  showMessageDialog(messageIndex);
}
function showMessageDialogSelect (event) {
  showMessageDialog(event.target.value);
}

function showMessageDialog(messageIndex) {
  hideMessageDialog();
  const maxT = getMaxT();
  document.getElementById('tValue').setAttribute('max', maxT);
  document.getElementById('rtValue').setAttribute('max', maxT);
  document.getElementById('showSyncResponse').style.display = "none";
  document.getElementById('syncResponse').style.display = "none";
  document.getElementById('showResponse').checked = false;
  document.getElementById('responseText').value = '';
  document.getElementById('rtValue').value = '';
  if (isNaN(parseInt(messageIndex))) {
    resetMessageDialog();
  } else {
    populateMessageDialog(messageIndex);
    const messageSvg = document.getElementById('message_' + messageIndex);
    messageSvg.setAttributeNS(null, 'filter', 'url(#dropshadow)');
  }
  document.getElementById('messageDialog').style.visibility = 'visible';
}

function resetMessageDialog() {
  document.getElementById('messageDialogHeader').textContent = 'New Message';
  document.getElementById('messageIdx').value = 'new';
  document.getElementById('messageType').selectedIndex = -1;
  document.getElementById('messageText').value = '';
  document.getElementById('tValue').value = '';
  document.getElementById('deleteMessageDialogBtn').setAttribute('hidden', 'hidden');
  document.getElementById('fromLifeline').selectedIndex = -1;
  document.getElementById('toLifeline').selectedIndex = -1;
  disableApplyMessageDialog();
}

function populateMessageDialog(messageIdx) {
  document.getElementById('messageDialogHeader').textContent = 'Edit Message';
  const messageData = theSourceDoc.dom.getElementsByTagName("message")[messageIdx];
//  const s = new XMLSerializer();
//  const content = s.serializeToString(lifelineData);
//  console.log(content);
  document.getElementById('messageIdx').value = messageIdx;
  document.getElementById('fromLifeline').selectedIndex = messageData.getAttribute('from');
  document.getElementById('messageType').value = messageData.getAttribute('type');
  messageTypeTailorDialog(messageData.getAttribute('type'));
  if (messageData.getAttribute('to') != null) {
    document.getElementById('toLifeline').selectedIndex = messageData.getAttribute('to');
  }
  document.getElementById('messageText').value = messageData.getElementsByTagName('messagetext')[0].textContent;
  document.getElementById('tValue').value = messageData.getAttribute('t');
  if (messageData.getElementsByTagName('response').length) {
    document.getElementById('showResponse').checked = true;
    document.getElementById('syncResponse').style.display = "inline-block";
    const responseTag = messageData.getElementsByTagName('response')[0];
    document.getElementById('responseText').value = responseTag.textContent;
    document.getElementById('rtValue').value = responseTag.getAttribute('t');
  }
  document.getElementById('deleteMessageDialogBtn').removeAttribute('hidden');
  disableApplyMessageDialog();
}

function hideMessageDialog() {
  document.getElementById('messageDialog').style.visibility = 'hidden';
  const messageIndex = document.getElementById('messageIdx');
  //console.log(parseInt(messageIndex.value));
  const messageSvg = document.getElementById('message_' + messageIndex.value);
  if (messageSvg != null) {
    messageSvg.removeAttribute('filter');
  }
}

function enableApplyMessageDialog() {
  // could do cross-field validations here
  if (document.getElementById('messageType').selectedIndex == '-1') {
    alert('please select a message type');
  } else {
    document.getElementById('applyMessageDialogBtn').disabled = false;
  }
}

function disableApplyMessageDialog() {
  document.getElementById('applyMessageDialogBtn').disabled = true;
}

function showFrameDialogSvg(event) {
  const frameIndex = event.target.parentElement.id.split('_')[1];
  showFrameDialog(frameIndex);
}

function showFrameDialogSelect(event) {
  showFrameDialog(event.target.value);
  //console.log(event.target.value);
}

function showFrameDialog(frameIndex) {
  hideFrameDialog();
  const maxT = getMaxT();
  document.getElementById('topT').setAttribute('max', maxT - 2);
  document.getElementById('bottomT').setAttribute('max', maxT);
  if (isNaN(parseInt(frameIndex))) {
    resetFrameDialog();
  } else {
    populateFrameDialog(frameIndex);
    const frameSvg = document.getElementById('frame_' + frameIndex);
    frameSvg.setAttributeNS(null, 'filter', 'url(#dropshadow)');
  }
  document.getElementById('frameDialog').style.visibility = 'visible';
}

function resetFrameDialog() {
  document.getElementById('frameDialogHeader').textContent = 'New Frame';
  document.getElementById('frameIdx').value = 'new';
  document.getElementById('frameType').selectedIndex = '-1';
  document.getElementById('frameText').value = '';
  document.getElementById('textWidth').value = '';
  document.getElementById('leftLifeline').selectedIndex = '-1';
  document.getElementById('rightLifeline').selectedIndex = '-1';
  document.getElementById('topT').value = '';
  document.getElementById('bottomT').value = '';
  document.getElementById('narrowFrame').checked = false;
  document.getElementById('altText').value = '';
  document.getElementById('altT').value = '';
  disableApplyFrameDialog();
}

function populateFrameDialog(frameIdx) {
  document.getElementById('frameDialogHeader').textContent = 'Edit Frame';
  const frameData = theSourceDoc.dom.getElementsByTagName("frame")[frameIdx];
  const s = new XMLSerializer();
  const content = s.serializeToString(frameData);
  document.getElementById('frameIdx').value = frameIdx;
  document.getElementById('frameType').value = frameData.getAttribute('type');
  frameTypeTailorDialog(frameData.getAttribute('type'));
  if (frameData.childNodes[0].nodeValue != null) { document.getElementById('frameText').value = frameData.childNodes[0].nodeValue; }
  if (frameData.getAttribute('widthfactor') != null) { document.getElementById('textWidth').value = frameData.getAttribute('widthfactor'); }
  if (frameData.getAttribute('left') != null) { document.getElementById('leftLifeline').selectedIndex = frameData.getAttribute('left'); }
  if (frameData.getAttribute('right') != null) { document.getElementById('rightLifeline').selectedIndex = frameData.getAttribute('right'); }
  if (frameData.getAttribute('top') != null) { document.getElementById('topT').value = frameData.getAttribute('top'); }
  if (frameData.getAttribute('bottom') != null) { document.getElementById('bottomT').value = frameData.getAttribute('bottom'); }
  if (frameData.getAttribute('narrow') == 'true') { document.getElementById('narrowFrame').checked = true; } else { document.getElementById('narrowFrame').checked = false; }
  if (frameData.getAttribute('alttext') != null) { document.getElementById('altText').value = frameData.getAttribute('alttext'); }
  if (frameData.getAttribute('altt') != null) { document.getElementById('altT').value = frameData.getAttribute('altt'); }
  document.getElementById('deleteFrameDialogBtn').removeAttribute('hidden');
  disableApplyFrameDialog();
}

function hideFrameDialog() {
  document.getElementById('frameDialog').style.visibility = 'hidden';
  const frameIndex = document.getElementById('frameIdx');
  const frameSvg = document.getElementById('frame_' + frameIndex.value);
  if (frameSvg != null) {
    frameSvg.removeAttribute('filter');
  }
}
function enableApplyFrameDialog() {
  // could do cross-field validations here
  if (document.getElementById('frameType').selectedIndex == '-1') {
    alert('please select a frame type');
  } else {
    document.getElementById('applyFrameDialogBtn').disabled = false;
  }
}

function disableApplyFrameDialog() {
  document.getElementById('applyFrameDialogBtn').disabled = true;
}
function startDragging(event) {
  document.addEventListener("mousemove", dragDialog);
}

function stopDragging(event) {
  document.removeEventListener("mousemove", dragDialog);
}

function dragDialog(event) {
  let dialog = event.target.parentElement;
  let styles = dialog.getBoundingClientRect();
  let left = styles.left;
  let top = styles.top;
  let height = styles.height;

  dialog.style.setProperty("left", `${left + event.movementX}px`);
  dialog.style.setProperty("top", `${top + event.movementY}px`);
}

function removeActivityBar(event) {
    const barId = 'barRow_' + event.target.value;
    document.getElementById(barId).remove();
    enableApplyLifelineDialog();
}

function bbarInput(event) {
  //console.log('get here');
  //console.log(event.currentTarget.value);
  const ebar = document.getElementById('ebar');
  const ebarMinValue = parseInt(event.currentTarget.value) + 1;
  ebar.setAttribute('min', ebarMinValue);
  if (ebar.value < ebarMinValue) {
    ebar.value = ebarMinValue;
  }
  enableApplyLifelineDialog();
}

function toggleNewActBar(event) {
  if(event.currentTarget.checked == true)
  {
    document.getElementById('newActBar').style.display = "inline-block";
  } else {
    document.getElementById('newActBar').style.display = "none";
  }
  //enableApplyLifelineDialog();
}

function toggleFiniteVisibility(event) {
  if(event.currentTarget.checked == true)
  {
    document.getElementById('finiteLifeline').style.display = "inline-block";
  } else {
    document.getElementById('finiteLifeline').style.display = "none";
    enableApplyLifelineDialog();
  }
}

function messageTypeTailorDialogHandler(event) {
  messageTypeTailorDialog(event.currentTarget.value);
}

function messageTypeTailorDialog(messageType) {
  switch (messageType) {
    case 'synchronous':
      document.getElementById('showSyncResponse').checked == false
      document.getElementById('showSyncResponse').style.display = "inline-block";
      document.getElementById('toLifeline').style.display = "inline-block";
      break;
    case 'reflexive':
      document.getElementById('showSyncResponse').style.display = "none";
      document.getElementById('syncResponse').style.display = "none";
      document.getElementById('toLifeline').style.display = "none";
      break;
    default:
      document.getElementById('showSyncResponse').style.display = "none";
      document.getElementById('syncResponse').style.display = "none";
      document.getElementById('toLifeline').style.display = "inline-block";
  }
  enableApplyMessageDialog();
}

function frameTypeTailorDialogHandler(event) {
  frameTypeTailorDialog(event.currentTarget.value);
}

function frameTypeTailorDialog(frameType) {
  switch (frameType) {
    case 'SD':
      document.getElementById('sd-div').style.display = "inline-block";
      document.getElementById('non-sd-div').style.display = "none";
      document.getElementById('alt-div').style.display = "none";
      break;
    case 'ALT':
      document.getElementById('sd-div').style.display = "none";
      document.getElementById('non-sd-div').style.display = "inline-block";
      document.getElementById('alt-div').style.display = "inline-block";
      break;
    default:
      document.getElementById('sd-div').style.display = "none";
      document.getElementById('non-sd-div').style.display = "inline-block";
      document.getElementById('alt-div').style.display = "none";
  }
  enableApplyFrameDialog();
}

function toggleResponseVisibility(event) {
  if(event.currentTarget.checked == true)
  {
    document.getElementById('syncResponse').style.display = "inline-block";
  } else {
    document.getElementById('syncResponse').style.display = "none";
  }
  enableApplyMessageDialog();
}


function tValueInput(event) {
  const rtValue = document.getElementById('rtValue');
  const rtMinValue = parseInt(event.currentTarget.value) + 1;
  rtValue.setAttribute('min', rtMinValue);
  if (rtValue.value < rtMinValue) {
    rtValue.value = rtMinValue;
  }
  enableApplyMessageDialog();
}

function topTInput(event) {
  const bottomTValue = document.getElementById('bottomT');
  const bottomTMinValue = parseInt(event.currentTarget.value) + 2;
  bottomTValue.setAttribute('min', bottomTMinValue);
  if (bottomTValue.value < bottomTMinValue) {
    bottomTValue.value = bottomTMinValue;
  }
  const altTValue = document.getElementById('altT');
  const altTMinValue = parseInt(event.currentTarget.value) + 1;
  altTValue.setAttribute('min', altTMinValue);
  if (altTValue.value < altTMinValue) {
    altTValue.value = altTMinValue;
  }
  enableApplyFrameDialog();
}

function updateLifeline() {
  const xmlDoc = document.implementation.createDocument("", "", null);
  const newElement = xmlDoc.createElement('lifeline');
  const typeAttr = document.getElementById('lifelineType').value;
  newElement.setAttribute('type',typeAttr);
  if (document.getElementById('showFiniteLifeline').checked) {
    const destroyT = document.getElementById('destroyT').value;
    newElement.setAttribute('destroy_t',destroyT);
  }
  const newLifelineName = xmlDoc.createElement('lifelinename');
  const lifelineName = document.getElementById('lifelineName').value;
  const newLifelineNameText = xmlDoc.createTextNode(lifelineName);
  newLifelineName.appendChild(newLifelineNameText);
  newElement.appendChild(newLifelineName);

  const newActivityBars = xmlDoc.createElement('activitybars');
  const barList = document.querySelectorAll('.barRow');
  outerLoop:
  for (let i = 0; i < barList.length; i++) {
    const activityBar = xmlDoc.createElement('activitybar');
    const begin_tValue = barList[i].firstChild.textContent;
    const end_tValue = barList[i].children[1].textContent;
    activityBar.setAttribute('begin_t', begin_tValue);
    activityBar.setAttribute('end_t', end_tValue);
    newActivityBars.appendChild(activityBar);
  }
  // add new bar here
  let inserted = false;
  if (document.getElementById('showNewActBar').checked) {
    const newActivityBar = xmlDoc.createElement('activitybar');
    const newBegin_tValue = parseInt(document.getElementById('bbar').value);
    const newEnd_tValue = parseInt(document.getElementById('ebar').value);
    newActivityBar.setAttribute('begin_t', newBegin_tValue);
    newActivityBar.setAttribute('end_t', newEnd_tValue);
    for (let j = 0; j < newActivityBars.childNodes.length; j++) {
      if (newBegin_tValue < parseInt(newActivityBars.childNodes[j].getAttribute('begin_t'))) {
        newActivityBars.insertBefore(newActivityBar, newActivityBars.children[j]);
        inserted = true;
        break
      }
    }
    if (inserted == false) {
      newActivityBars.appendChild(newActivityBar);
    }
  }

  newElement.appendChild(newActivityBars);
  //const s = new XMLSerializer();
  //const content = s.serializeToString(newElement);
  //console.log(content);
  const lifelineIdx = document.getElementById('lifelineIdx');
  const lifelineList = theSourceDoc.dom.getElementsByTagName("lifelinelist")[0];
  if (isNaN(parseInt(lifelineIdx.value))) {
    // append if new.
    lifelineList.appendChild(newElement);
    // update Idx hidden text field
    lifelineIdx.value = lifelineList.childNodes.length - 1;
  } else {
    // replace if existing
    theOldLifeline = lifelineList.getElementsByTagName('lifeline')[lifelineIdx.value];
    lifelineList.replaceChild(newElement, theOldLifeline);
  }
  const lifelineData = theSourceDoc.dom.getElementsByTagName('lifeline')[lifelineIdx.value]
  const barData = lifelineData.getElementsByTagName('activitybars')[0].getElementsByTagName('activitybar');
  resetActivityBars(barData);
  theSourceDoc.isModified = true;
  populateUi();
  disableApplyLifelineDialog();
}

function okLifeline() {
  if (document.getElementById('applyLifelineDialogBtn').disabled == false) {
    updateLifeline();
  }
  hideLifelineDialog();
}

function deleteLifeline () {
  const lifelineIdx = document.getElementById('lifelineIdx');
  const lifelineList = theSourceDoc.dom.getElementsByTagName('lifelinelist')[0];
  const lifeline2BRemoved = lifelineList.getElementsByTagName('lifeline')[lifelineIdx.value];
  lifelineList.removeChild(lifeline2BRemoved);
  theSourceDoc.isModified = true;
  populateUi();
  hideLifelineDialog();
}

function updateMessage() {
  let xmlDoc = document.implementation.createDocument("", "", null);
  let newElement = xmlDoc.createElement('message');
  const typeAttr = document.getElementById('messageType').value;
  const fromAttr = document.getElementById('fromLifeline').value;
  const tAttr = document.getElementById('tValue').value;
  newElement.setAttribute('type',typeAttr);
  newElement.setAttribute('from',fromAttr);
  if (!(typeAttr == 'reflexive')) {
    const toAttr = document.getElementById('toLifeline').value;
    newElement.setAttribute('to',toAttr);
  }
  newElement.setAttribute('t',tAttr);
  let newMessageText = xmlDoc.createElement('messagetext');
  const messageText = document.getElementById('messageText').value;
  const newMessageTextTextNode = xmlDoc.createTextNode(messageText);
  newMessageText.appendChild(newMessageTextTextNode);
  newElement.appendChild(newMessageText);
  if (typeAttr == 'synchronous' && document.getElementById('showResponse').checked == true) {
    let newResponse = xmlDoc.createElement('response');
    const tResponseAttr = document.getElementById('rtValue').value;
    newResponse.setAttribute('t', tResponseAttr);
    const responseText = document.getElementById('responseText').value;
    const newResponseTextNode = xmlDoc.createTextNode(responseText);
    newResponse.appendChild(newResponseTextNode);
    newElement.appendChild(newResponse);
  }
  let messageIdx = document.getElementById('messageIdx');

  const messageList = theSourceDoc.dom.getElementsByTagName("messagelist")[0];
  messages = messageList.getElementsByTagName('message')
  if (!(isNaN(parseInt(messageIdx.value)))) {
    const message2BRemoved = messages[messageIdx.value];
    messageList.removeChild(message2BRemoved);
  }
  let inserted = false;
  for (i = 0; i < messages.length; i++) {
    if (parseInt(tAttr) < parseInt(messages[i].getAttribute('t'))) {
      messageList.insertBefore(newElement, messages[i]);
      messageIdx.value = i;
      inserted = true;
      break;
    }
  }
  if (inserted == false) {
    messageIdx.value = messages.length;
    messageList.appendChild(newElement);
  }
  theSourceDoc.isModified = true;
  populateUi();
}


function okMessage() {
  if (document.getElementById('applyMessageDialogBtn').disabled == false) {
    updateMessage();
  }
  hideMessageDialog();
}

function deleteMessage () {
  const messageIdx = document.getElementById('messageIdx');
  const messageList = theSourceDoc.dom.getElementsByTagName('messagelist')[0];
  const message2BRemoved = messageList.getElementsByTagName('message')[messageIdx.value];
  messageList.removeChild(message2BRemoved);
  theSourceDoc.isModified = true;
  populateUi();
  hideMessageDialog();
}

function updateFrame() {
  let xmlDoc = document.implementation.createDocument("", "", null);
  let newElement = xmlDoc.createElement('frame');
  const frameTextValue = document.getElementById('frameText').value;
  const newFrameTextNode = xmlDoc.createTextNode(frameTextValue);
  newElement.appendChild(newFrameTextNode);
  const typeAttr = document.getElementById('frameType').value;
  newElement.setAttribute('type', typeAttr);
  if (typeAttr == 'SD') {
    newElement.setAttribute('widthfactor', document.getElementById('textWidth').value);
  } else {
    newElement.setAttribute('left', document.getElementById('leftLifeline').value);
    newElement.setAttribute('right', document.getElementById('rightLifeline').value);
    newElement.setAttribute('top', document.getElementById('topT').value);
    newElement.setAttribute('bottom', document.getElementById('bottomT').value);
  }
  if (typeAttr == 'ALT') {
    newElement.setAttribute('alttext', document.getElementById('altText').value);
    newElement.setAttribute('altt', document.getElementById('altT').value);
  }
  if (document.getElementById('narrowFrame').checked = true) {
    newElement.setAttribute('narrow', 'true');
  }
  const frameIdx = document.getElementById('frameIdx');
  const frameList = theSourceDoc.dom.getElementsByTagName("framelist")[0];
  if (isNaN(parseInt(frameIdx.value))) {
    // append if new.
    frameList.appendChild(newElement);
    // update Idx hidden text field
    frameIdx.value = frameList.childNodes.length - 1;
  } else {
    // replace if existing
    theOldFrame = frameList.getElementsByTagName('frame')[frameIdx.value];
    frameList.replaceChild(newElement, theOldFrame);
  }
  theSourceDoc.isModified = true;
  populateUi();
  disableApplyFrameDialog();
}


function okFrame() {
  if (document.getElementById('applyFrameDialogBtn').disabled == false) {
    updateFrame();
  }
  hideFrameDialog();
}

function deleteFrame () {
  const frameIdx = document.getElementById('frameIdx');
  const frameList = theSourceDoc.dom.getElementsByTagName('framelist')[0];
  const frame2BRemoved = frameList.getElementsByTagName('frame')[frameIdx.value];
  frameList.removeChild(frame2BRemoved);
  theSourceDoc.isModified = true;
  populateUi();
  hideFrameDialog();
}

function showLayoutDialog() {
  populateLayoutDialog();
  document.getElementById('layoutDialog').style.visibility = 'visible';
}

function hideLayoutDialog() {
  document.getElementById('layoutDialog').style.visibility = 'hidden';
}

function populateLayoutDialog() {
    const hSpacing = document.getElementById('hSpacing');
    const hSpacingValue = document.getElementById('hSpacingValue');
    hSpacingValue.innerText = hSpacing.value = theSourceDoc.dom.getElementsByTagName("hspacing")[0].childNodes[0].nodeValue;

    const vSpacing = document.getElementById('vSpacing');
    const vSpacingValue = document.getElementById('vSpacingValue');
    vSpacingValue.innerText = vSpacing.value = theSourceDoc.dom.getElementsByTagName("vspacing")[0].childNodes[0].nodeValue;

    const maxT = document.getElementById('maxT');
    const maxTValue = document.getElementById('maxTValue');
    maxTValue.innerText = maxT.value = theSourceDoc.dom.getElementsByTagName("max_t")[0].childNodes[0].nodeValue;

    const fontSize = document.getElementById('fontSize');
    const fontSizeValue = document.getElementById('fontSizeValue');
    fontSizeValue.innerText = fontSize.value = theSourceDoc.dom.getElementsByTagName("fontsize")[0].childNodes[0].nodeValue;
}

function updateHSpacing(event) {
  const hspacing = theSourceDoc.dom.getElementsByTagName('hspacing')[0]
  hspacing.childNodes[0].nodeValue = event.target.value;
  theSourceDoc.isModified = true;
  document.getElementById('hSpacingValue').innerText = event.target.value;
  populateUi();
}

function updateVSpacing(event) {
  const vspacing = theSourceDoc.dom.getElementsByTagName('vspacing')[0]
  vspacing.childNodes[0].nodeValue = event.target.value;
  theSourceDoc.isModified = true;
  document.getElementById('vSpacingValue').innerText = event.target.value;
  populateUi();
}

function updateMaxT(event) {
  const max_t = theSourceDoc.dom.getElementsByTagName('max_t')[0]
  max_t.childNodes[0].nodeValue = event.target.value;
  theSourceDoc.isModified = true;
  document.getElementById('maxTValue').innerText = event.target.value;
  populateUi();
}

function updateFontSize(event) {
  const fontsize = theSourceDoc.dom.getElementsByTagName('fontsize')[0]
  fontsize.childNodes[0].nodeValue = event.target.value;
  theSourceDoc.isModified = true;
  document.getElementById('fontSizeValue').innerText = event.target.value;
  populateUi();
}

function check4Changes (event) {
  if (theSourceDoc.isModified == true) {
    event.preventDefault();
    event.returnValue = 'You have unfinished changes!';
  }
}

// Add handlers
document.onreadystatechange = () => {
  if (document.readyState === "complete") {
    // Top Menu
    const inputElement = document.getElementById("load_local");
    inputElement.addEventListener("change", loadFileDocument, false);
    const exampleElement = document.getElementById("load_example");
    exampleElement.addEventListener("click", loadExampleDocument, false);
    const saveUmlElement = document.getElementById("save_uml");
    saveUmlElement.addEventListener("click", saveUmlDocument, false);
    const saveSvgElement = document.getElementById("save_svg");
    saveSvgElement.addEventListener("click", saveSvgDocument, false);
    document.addEventListener('mouseup', stopDragging);

    const scaling = document.getElementById('scaling');
    scaling.addEventListener('input', updateScale);

    const tAxisBtn = document.getElementById('toggleScaleButton');
    tAxisBtn.addEventListener('click', tAxisShow);

    const layoutBtn = document.getElementById('layoutButton')
    layoutBtn.addEventListener('click', showLayoutDialog);
    const hideLayoutBtn = document.getElementById('hideLayoutDialogBtn');
    hideLayoutBtn.addEventListener('click', hideLayoutDialog);

    const hSpacing = document.getElementById('hSpacing');
    hSpacing.addEventListener('input', updateHSpacing);
    const vSpacing = document.getElementById('vSpacing');
    vSpacing.addEventListener('input', updateVSpacing);
    const maxT = document.getElementById('maxT');
    maxT.addEventListener('input', updateMaxT);
    const fontSize = document.getElementById('fontSize');
    fontSize.addEventListener('input', updateFontSize);
    const layoutDialogHeader = document.getElementById('layoutDialogHeader');
    layoutDialogHeader.addEventListener('mousedown', startDragging);


    const lifelines = document.getElementById('lifelines');
    lifelines.addEventListener('click', showLifelineDialogSelect);
    const lifelineDialogHeader = document.getElementById('lifelineDialogHeader');
    lifelineDialogHeader.addEventListener('mousedown', startDragging);
    const lifelineName = document.getElementById('lifelineName');
    lifelineName.addEventListener('change', enableApplyLifelineDialog);
    const lifelineType = document.getElementById('lifelineType');
    lifelineType.addEventListener('change', enableApplyLifelineDialog);
    const hideDialog = document.getElementById('cancelLifelineDialogBtn');
    hideDialog.addEventListener('click', hideLifelineDialog);
    const applyDialog = document.getElementById('applyLifelineDialogBtn');
    applyDialog.addEventListener('click', updateLifeline);
    const okDialog = document.getElementById('okLifelineDialogBtn');
    okDialog.addEventListener('click', okLifeline);
    const deleteDialog = document.getElementById('deleteLifelineDialogBtn');
    deleteDialog.addEventListener('click', deleteLifeline);
    const showNewActBar = document.getElementById('showNewActBar');
    showNewActBar.addEventListener('click', toggleNewActBar);
    const bbar = document.getElementById('bbar');
    bbar.addEventListener('input', bbarInput);
    const showFinite = document.getElementById('showFiniteLifeline');
    showFinite.addEventListener('click', toggleFiniteVisibility);
    const destroyT = document.getElementById('destroyT');
    destroyT.addEventListener('change', enableApplyLifelineDialog);

    const messages = document.getElementById('messages');
    messages.addEventListener('click', showMessageDialogSelect);
    const messageDialogHeader = document.getElementById('messageDialogHeader');
    messageDialogHeader.addEventListener('mousedown', startDragging);
    const messageFrom = document.getElementById('fromLifeline');
    messageFrom.addEventListener('change', enableApplyMessageDialog);
    const messageTo = document.getElementById('toLifeline');
    messageTo.addEventListener('change', enableApplyMessageDialog);
    const messageText = document.getElementById('messageText');
    messageText.addEventListener('change', enableApplyMessageDialog);
    const messageT = document.getElementById('tValue');
    messageT.addEventListener('input', tValueInput);
    const messageResponse = document.getElementById('responseText');
    messageResponse.addEventListener('change', enableApplyMessageDialog);
    const rtValue = document.getElementById('rtValue');
    rtValue.addEventListener('change', enableApplyMessageDialog);
    const hideMsgDialog = document.getElementById('cancelMessageDialogBtn');
    hideMsgDialog.addEventListener('click', hideMessageDialog);
    const messageType = document.getElementById('messageType');
    messageType.addEventListener('change', messageTypeTailorDialogHandler);
    const showResponse = document.getElementById('showResponse');
    showResponse.addEventListener('click', toggleResponseVisibility);
    const applyMDialog = document.getElementById('applyMessageDialogBtn');
    applyMDialog.addEventListener('click', updateMessage);
    const okMDialog = document.getElementById('okMessageDialogBtn');
    okMDialog.addEventListener('click', okMessage);
    const deleteMDialog = document.getElementById('deleteMessageDialogBtn');
    deleteMDialog.addEventListener('click', deleteMessage);

    const frames = document.getElementById('frames');
    frames.addEventListener('click', showFrameDialogSelect);
    const frameDialogHeader = document.getElementById('frameDialogHeader');
    frameDialogHeader.addEventListener('mousedown', startDragging);
    const frameTxt = document.getElementById('frameText');
    frameTxt.addEventListener('change', enableApplyFrameDialog);
    const textWidth = document.getElementById('textWidth');
    textWidth.addEventListener('change', enableApplyFrameDialog);
    const lftLiifeline = document.getElementById('leftLifeline');
    lftLiifeline.addEventListener('change', enableApplyFrameDialog);
    const rghtLifeline = document.getElementById('rightLifeline');
    rghtLifeline.addEventListener('change', enableApplyFrameDialog);

    const topT = document.getElementById('topT');
    //topT.addEventListener('change', enableApplyFrameDialog);
    topT.addEventListener('input', topTInput);
    const bottomT = document.getElementById('bottomT');
    bottomT.addEventListener('change', enableApplyFrameDialog);
    const altText = document.getElementById('altText');
    altText.addEventListener('change', enableApplyFrameDialog);
    const altT = document.getElementById('altT');
    altT.addEventListener('change', enableApplyFrameDialog);
    const hideFDialog = document.getElementById('cancelFrameDialogBtn');
    hideFDialog.addEventListener('click', hideFrameDialog);
    const frameType = document.getElementById('frameType');
    frameType.addEventListener('change', frameTypeTailorDialogHandler);
    const applyFDialog = document.getElementById('applyFrameDialogBtn');
    applyFDialog.addEventListener('click', updateFrame);
    const okFDialog = document.getElementById('okFrameDialogBtn');
    okFDialog.addEventListener('click', okFrame);
    const deleteFDialog = document.getElementById('deleteFrameDialogBtn');
    deleteFDialog.addEventListener('click', deleteFrame);

    window.addEventListener("beforeunload", check4Changes);
  }
};
