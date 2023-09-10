<?xml version="1.0" encoding="UTF-8"?>
<xsl:stylesheet version="1.0" xmlns:xsl="http://www.w3.org/1999/XSL/Transform"  xmlns="http://www.w3.org/2000/svg">
  <xsl:param  name="SHOWSCALE" select="''"/>
  <xsl:param  name="SCALEFACTOR" select="1"/>
  <!-- invisible bounding rects to make it easier to click on lines -->
  <xsl:param  name="BOUNDINGRECTS" select="'yes'"/>
  <!-- space between lifelines -->
  <xsl:variable name="HSPACING" select="/sequencediagml/parameters/hspacing/text()"/>
  <!-- space between increments of t -->
  <xsl:variable name="VSPACING" select="/sequencediagml/parameters/vspacing/text()"/>
  <xsl:variable name="SVGWIDTH">
    <xsl:choose>
      <xsl:when test="count(/sequencediagml/lifelinelist/lifeline) > 1">
        <xsl:value-of select="$HSPACING * count(/sequencediagml/lifelinelist/lifeline)"/>
      </xsl:when>
      <xsl:otherwise>
        <xsl:value-of select="$HSPACING * 2"/>
      </xsl:otherwise>
    </xsl:choose>
  </xsl:variable>
  <xsl:variable name="VOFFSET" select="-160"/>
  <xsl:variable name="MAXT" select="/sequencediagml/parameters/max_t/text()"/>
  <xsl:variable name="SVGHEIGHT" select="($VSPACING * ($MAXT + 1)) - $VOFFSET"/>
  <xsl:variable name="ACTIVITYBARWIDTH" select="20"/>
  <xsl:variable name="FONTSIZE" select="/sequencediagml/parameters/fontsize/text()"/>
  <xsl:variable name="FONTSTRING" select="concat('font-size: ', $FONTSIZE, 'pt;')"/>
  <xsl:template match="/">
    <xsl:element name="svg">
      <xsl:attribute name="width"><xsl:value-of select="$SVGWIDTH * $SCALEFACTOR"/></xsl:attribute>
      <xsl:attribute name="height"><xsl:value-of select="$SVGHEIGHT * $SCALEFACTOR"/></xsl:attribute>
      <xsl:attribute name="viewBox"><xsl:value-of select="concat(-$HSPACING div 2, ' ', $VOFFSET, ' ', $SVGWIDTH, ' ', $SVGHEIGHT)"/></xsl:attribute>
      <defs>
        <marker id="arrowhead-solid" markerWidth="10" markerHeight="7" refX="10" refY="3.5" orient="auto">
          <polygon points="0 0, 10 3.5, 0 7" />
        </marker>
        <marker id="arrowhead" markerWidth="10" markerHeight="7" refX="10" refY="3.5" orient="auto">
          <line x1="0" y1="0" x2="10" y2="3.5" style="stroke:black;"/>
          <line x1="0" y1="7" x2="10" y2="3.5" style="stroke:black;"/>
        </marker>
        <symbol id="object-rect" style="stroke: black; fill: none; stroke-width: 2;">
          <xsl:element name="rect">
            <xsl:attribute name="x"><xsl:value-of select="$HSPACING * 0.6"/></xsl:attribute>
            <xsl:attribute name="y">1</xsl:attribute>
            <xsl:attribute name="width"><xsl:value-of select="$HSPACING * 0.8"/></xsl:attribute>
            <xsl:attribute name="height">100</xsl:attribute>
          </xsl:element>
        </symbol>
        <symbol id="frame-polygon" style="stroke: black; fill: white; stroke-width: 2;">
          <polygon points="0,0 80,0 80,15 70,30 0,30"/>
        </symbol>
        <symbol id="actor" style="stroke: black; fill: none; stroke-width: 2;">
          <xsl:element name="circle">
            <xsl:attribute name="cx"><xsl:value-of select="$HSPACING"/></xsl:attribute>
            <xsl:attribute name="cy">20</xsl:attribute>
            <xsl:attribute name="r">10</xsl:attribute>
          </xsl:element>
          <xsl:element name="line">
            <xsl:attribute name="x1"><xsl:value-of select="$HSPACING"/></xsl:attribute>
            <xsl:attribute name="y1">30</xsl:attribute>
            <xsl:attribute name="x2"><xsl:value-of select="$HSPACING"/></xsl:attribute>
            <xsl:attribute name="y2">55</xsl:attribute>
          </xsl:element>
          <xsl:element name="line">
            <xsl:attribute name="x1"><xsl:value-of select="$HSPACING - 15"/></xsl:attribute>
            <xsl:attribute name="y1">35</xsl:attribute>
            <xsl:attribute name="x2"><xsl:value-of select="$HSPACING + 15"/></xsl:attribute>
            <xsl:attribute name="y2">35</xsl:attribute>
          </xsl:element>
          <xsl:element name="line">
            <xsl:attribute name="x1"><xsl:value-of select="$HSPACING"/></xsl:attribute>
            <xsl:attribute name="y1">55</xsl:attribute>
            <xsl:attribute name="x2"><xsl:value-of select="$HSPACING - 15"/></xsl:attribute>
            <xsl:attribute name="y2">75</xsl:attribute>
          </xsl:element>
          <xsl:element name="line">
            <xsl:attribute name="x1"><xsl:value-of select="$HSPACING"/></xsl:attribute>
            <xsl:attribute name="y1">55</xsl:attribute>
            <xsl:attribute name="x2"><xsl:value-of select="$HSPACING + 15"/></xsl:attribute>
            <xsl:attribute name="y2">75</xsl:attribute>
          </xsl:element>
        </symbol>
        <symbol id="reflexive" style="stroke: black; fill: none; stroke-width: 2;">
          <xsl:element name="line">
            <xsl:attribute name="x1">0</xsl:attribute>
            <xsl:attribute name="y1"><xsl:value-of select="$VSPACING"/></xsl:attribute>
            <xsl:attribute name="x2"><xsl:value-of select="$HSPACING div 5"/></xsl:attribute>
            <xsl:attribute name="y2"><xsl:value-of select="$VSPACING"/></xsl:attribute>
          </xsl:element>
          <xsl:element name="line">
            <xsl:attribute name="x1"><xsl:value-of select="$HSPACING div 5"/></xsl:attribute>
            <xsl:attribute name="y1"><xsl:value-of select="$VSPACING"/></xsl:attribute>
            <xsl:attribute name="x2"><xsl:value-of select="$HSPACING div 5"/></xsl:attribute>
            <xsl:attribute name="y2"><xsl:value-of select="$VSPACING * 2"/></xsl:attribute>
          </xsl:element>
          <xsl:element name="line">
            <xsl:attribute name="x1"><xsl:value-of select="$HSPACING div 5"/></xsl:attribute>
            <xsl:attribute name="y1"><xsl:value-of select="$VSPACING * 2"/></xsl:attribute>
            <xsl:attribute name="x2">0</xsl:attribute>
            <xsl:attribute name="y2"><xsl:value-of select="$VSPACING * 2"/></xsl:attribute>
            <xsl:attribute name="marker-end">url(#arrowhead-solid)</xsl:attribute>
          </xsl:element>
          <xsl:element name="rect">
            <xsl:attribute name="x">0</xsl:attribute>
            <xsl:attribute name="y"><xsl:value-of select="$VSPACING"/></xsl:attribute>
            <xsl:attribute name="width"><xsl:value-of select="$HSPACING div 5"/></xsl:attribute>
            <xsl:attribute name="height"><xsl:value-of select="$VSPACING"/></xsl:attribute>
            <xsl:attribute name="visibility">hidden</xsl:attribute>
          </xsl:element>
        </symbol>
        <symbol id="destroy-symbol" width="20" height="20" style="stroke: black; fill: none; stroke-width: 4;" viewBox="0 0 20 20">
          <line x1="0" y1="0" x2="20" y2="20"/>
          <line x1="20" y1="0" x2="0" y2="20"/>
        </symbol>
        <filter x="0" y="0" width="1" height="1" id="textbg">
          <feFlood flood-color="white" result="bg" flood-opacity="0.6"/>
          <feMerge>
            <feMergeNode in="bg"/>
            <feMergeNode in="SourceGraphic"/>
          </feMerge>
        </filter>
        <filter id="dropshadow" x="0" y="0"  width="200%" height="200%">
          <feOffset result="offOut" in="SourceGraphic" dx="4" dy="4" />
          <feGaussianBlur result="blurOut" in="offOut" stdDeviation="4" />
          <feBlend in="SourceGraphic" in2="blurOut" mode="normal" />
        </filter>
      </defs>

      <xsl:apply-templates select="/sequencediagml/lifelinelist/lifeline"/>
      <xsl:apply-templates select="/sequencediagml/messagelist/message"/>
      <xsl:apply-templates select="/sequencediagml/framelist/frame"/>
      <xsl:if test="$SHOWSCALE">
        <xsl:element name="line">
          <xsl:attribute name="x1"><xsl:value-of select="10 - ($HSPACING div 2)"/></xsl:attribute>
          <xsl:attribute name="y1">0</xsl:attribute>
          <xsl:attribute name="x2"><xsl:value-of select="10 - ($HSPACING div 2)"/></xsl:attribute>
          <xsl:attribute name="y2"><xsl:value-of select="$MAXT * $VSPACING"/></xsl:attribute>
          <xsl:attribute name="style">stroke: grey; stroke-width: 2;</xsl:attribute>
        </xsl:element>
        <xsl:call-template name="tick">
          <xsl:with-param name="I"><xsl:value-of select="$MAXT"/></xsl:with-param>
        </xsl:call-template>
      </xsl:if>
    </xsl:element>
  </xsl:template>

  <xsl:template match="lifeline">
    <xsl:variable name="LIFELINEIDX" select="count(preceding-sibling::lifeline)"/>
    <xsl:variable name="HPOS" select="$LIFELINEIDX * $HSPACING"/>
    <xsl:variable name="HREF">
      <xsl:choose>
        <xsl:when test="@type = 'actor'"><xsl:value-of select="'#actor'"/></xsl:when>
        <xsl:when test="@type = 'object'"><xsl:value-of select="'#object-rect'"/></xsl:when>
        <xsl:otherwise><xsl:value-of select="'#object-rect'"/></xsl:otherwise>
      </xsl:choose>
    </xsl:variable>
    <xsl:variable name="CREATIONTIME">
      <xsl:choose>
        <xsl:when test="count(/sequencediagml/messagelist/message[@to = $LIFELINEIDX and @type = 'create'])"><xsl:value-of select="/sequencediagml/messagelist/message[@to = $LIFELINEIDX][1]/@t"/></xsl:when>
        <xsl:otherwise>0</xsl:otherwise>
      </xsl:choose>
    </xsl:variable>
    <xsl:variable name="OBJECTY">
      <xsl:choose>
        <xsl:when test="$CREATIONTIME > 0"><xsl:value-of select="($CREATIONTIME * $VSPACING) - 50"/></xsl:when>
        <xsl:otherwise>-100</xsl:otherwise>
      </xsl:choose>
    </xsl:variable>
    <xsl:variable name="TEXTPOSITION">
      <xsl:choose>
        <xsl:when test="(@type = 'actor') and ($CREATIONTIME = 0)"><xsl:value-of select="-10"/></xsl:when>
        <xsl:when test="(@type = 'object') and ($CREATIONTIME = 0)"><xsl:value-of select="-70"/></xsl:when>
        <xsl:when test="(@type = 'actor') and ($CREATIONTIME > 0)"><xsl:value-of select="($CREATIONTIME * $VSPACING)+40"/></xsl:when>
        <xsl:when test="(@type = 'object') and ($CREATIONTIME > 0)"><xsl:value-of select="($CREATIONTIME * $VSPACING)-20"/></xsl:when>
        <xsl:otherwise><xsl:value-of select="-70"/></xsl:otherwise>
      </xsl:choose>
    </xsl:variable>
    <xsl:variable name="LIFELINESTART">
      <xsl:choose>
        <xsl:when test="$CREATIONTIME > 0"><xsl:value-of select="($CREATIONTIME * $VSPACING) + 50"/></xsl:when>
        <xsl:otherwise>0</xsl:otherwise>
      </xsl:choose>
    </xsl:variable>
    <xsl:variable name="LIFELINEEND">
      <xsl:choose>
        <xsl:when test="@destroy_t &lt; $MAXT"><xsl:value-of select="@destroy_t * $VSPACING"/></xsl:when>
        <xsl:otherwise><xsl:value-of select="$MAXT * $VSPACING"/></xsl:otherwise>
      </xsl:choose>
    </xsl:variable>
    <xsl:element name="g">
      <xsl:attribute name="id"><xsl:value-of select="concat('lifeline_', $LIFELINEIDX)"/></xsl:attribute>
      <xsl:attribute name="pointer-events">all</xsl:attribute>
      <xsl:attribute name="style"><xsl:value-of select="$FONTSTRING"/></xsl:attribute>
      <xsl:element name="use">
        <xsl:attribute name="href"><xsl:value-of select="$HREF"/></xsl:attribute>
        <xsl:attribute name="x"><xsl:value-of select="$HPOS - $HSPACING"/></xsl:attribute>
        <xsl:attribute name="y"><xsl:value-of select="$OBJECTY"/></xsl:attribute>
      </xsl:element>
      <xsl:element name="line">
        <xsl:attribute name="x1"><xsl:value-of select="$HPOS"/></xsl:attribute>
        <xsl:attribute name="y1"><xsl:value-of select="$LIFELINESTART"/></xsl:attribute>
        <xsl:attribute name="x2"><xsl:value-of select="$HPOS"/></xsl:attribute>
        <xsl:attribute name="y2"><xsl:value-of select="$LIFELINEEND"/></xsl:attribute>
        <xsl:attribute name="style">stroke: black; stroke-width: 2; stroke-dasharray: 5 5;</xsl:attribute>
      </xsl:element>
      <xsl:element name="text">
        <xsl:attribute name="x"><xsl:value-of select="$HPOS"/></xsl:attribute>
        <xsl:attribute name="y"><xsl:value-of select="$TEXTPOSITION"/></xsl:attribute>
        <xsl:attribute name="style">text-anchor: middle;</xsl:attribute>
        <xsl:attribute name="filter">url(#textbg)</xsl:attribute>
        <xsl:choose>
          <xsl:when test="contains(lifelinename/text(),'&#10;')">
            <xsl:value-of select="substring-before(lifelinename/text(), '&#10;')"/>
            <xsl:call-template name="tspan">
              <xsl:with-param name="XPOS" select="$HPOS"/>
              <xsl:with-param name="TEXT" select="substring-after(lifelinename/text(), '&#10;')"/>
            </xsl:call-template>
          </xsl:when>
          <xsl:otherwise>
            <xsl:value-of select="lifelinename/text()"/>
          </xsl:otherwise>
        </xsl:choose>
      </xsl:element>
    <!-- draw activity bars -->
      <xsl:for-each select="activitybars/activitybar">
        <xsl:element name="rect">
          <xsl:attribute name="x"><xsl:value-of select="$HPOS - ($ACTIVITYBARWIDTH div 2)"/></xsl:attribute>
          <xsl:attribute name="y"><xsl:value-of select="$VSPACING * @begin_t"/></xsl:attribute>
          <xsl:attribute name="width"><xsl:value-of select="$ACTIVITYBARWIDTH"/></xsl:attribute>
          <xsl:attribute name="height"><xsl:value-of select="$VSPACING * (@end_t - @begin_t)"/></xsl:attribute>
          <xsl:attribute name="style">stroke: black; fill: white; stroke-width: 2;</xsl:attribute>
        </xsl:element>
      </xsl:for-each>
      <xsl:if test="@destroy_t &lt; $MAXT">
        <xsl:element name="use">
          <xsl:attribute name="href">#destroy-symbol</xsl:attribute>
          <xsl:attribute name="x"><xsl:value-of select="$HPOS - 10"/></xsl:attribute>
          <xsl:attribute name="y"><xsl:value-of select="$LIFELINEEND - 10"/></xsl:attribute>
        </xsl:element>
      </xsl:if>
    </xsl:element>
  </xsl:template>

  <xsl:template match="message">
    <xsl:variable name="MESSAGEIDX" select="count(preceding-sibling::message)"/>
    <xsl:variable name="MESSAGEOFFSET">
      <xsl:choose>
        <xsl:when test="@to > @from">
          <xsl:value-of select="$ACTIVITYBARWIDTH div 2"/>
        </xsl:when>
        <xsl:otherwise>
          <xsl:value-of select="$ACTIVITYBARWIDTH div -2"/>
        </xsl:otherwise>
      </xsl:choose>
    </xsl:variable>
    <xsl:variable name="MESSAGEOFFSETTO">
      <xsl:choose>
        <xsl:when test="@type = 'create'">
          <xsl:value-of select="($MESSAGEOFFSET div ($ACTIVITYBARWIDTH div 2)) * (0.4 * $HSPACING)"/>
        </xsl:when>
        <xsl:otherwise>
          <xsl:value-of select="$MESSAGEOFFSET"/>
        </xsl:otherwise>
      </xsl:choose>
    </xsl:variable>
    <xsl:variable name="XBOUNDRECT">
      <xsl:choose>
        <xsl:when test="@to > @from">
          <xsl:value-of select="(@from  * $HSPACING) + $MESSAGEOFFSET"/>
        </xsl:when>
        <xsl:otherwise>
          <xsl:value-of select="(@to * $HSPACING) - $MESSAGEOFFSET"/>
        </xsl:otherwise>
      </xsl:choose>
    </xsl:variable>
    <xsl:variable name="ABSMESSAGEOFFSETS" select="($MESSAGEOFFSET + $MESSAGEOFFSETTO)*($MESSAGEOFFSET + $MESSAGEOFFSETTO >= 0) - ($MESSAGEOFFSET + $MESSAGEOFFSETTO)*($MESSAGEOFFSET + $MESSAGEOFFSETTO &lt; 0)"/>
    <xsl:variable name="WIDTHBOUNDRECT" select="(((@from - @to)*((@from - @to) >=0) - (@from - @to)*((@from - @to) &lt; 0)) * $HSPACING) - $ABSMESSAGEOFFSETS"/>
    <xsl:variable name="ARROWTYPE">
      <xsl:choose>
        <xsl:when test="@type = 'asynchronous' or @type = 'create'">
          <xsl:value-of select="'url(#arrowhead)'"/>
        </xsl:when>
        <xsl:otherwise>
          <xsl:value-of select="'url(#arrowhead-solid)'"/>
        </xsl:otherwise>
      </xsl:choose>
    </xsl:variable>
    <xsl:variable name="LINESTROKE">
      <xsl:choose>
        <xsl:when test="@type = 'create'">
          <xsl:value-of select="'stroke: black; stroke-width: 2; stroke-dasharray: 5 5;'"/>
        </xsl:when>
        <xsl:otherwise>
          <xsl:value-of select="'stroke:black;stroke-width:2;'"/>
        </xsl:otherwise>
      </xsl:choose>
    </xsl:variable>

    <xsl:variable name="MESSAGEANCHOR"><xsl:value-of select="concat('text-anchor: ', substring('end;', 1 div (contains($MESSAGEOFFSET, '-'))), substring('start;', 1 div not(contains($MESSAGEOFFSET, '-'))))"/></xsl:variable>
    <xsl:variable name="RESPONSEANCHOR"><xsl:value-of select="concat('text-anchor: ', substring('start;', 1 div (contains($MESSAGEOFFSET, '-'))), substring('end;', 1 div not(contains($MESSAGEOFFSET, '-'))))"/></xsl:variable>
    <xsl:element name="g">
      <xsl:attribute name="id"><xsl:value-of select="concat('message_', $MESSAGEIDX)"/></xsl:attribute>
      <xsl:attribute name="pointer-events">all</xsl:attribute>
      <xsl:attribute name="style"><xsl:value-of select="$FONTSTRING"/></xsl:attribute>
      <xsl:choose>
        <xsl:when test="@type = 'reflexive'">
          <xsl:element name="use">
            <xsl:attribute name="href">#reflexive</xsl:attribute>
            <xsl:attribute name="x"><xsl:value-of select="(@from * $HSPACING) + ($ACTIVITYBARWIDTH div 2)"/></xsl:attribute>
            <xsl:attribute name="y"><xsl:value-of select="((@t - 1) * $VSPACING)"/></xsl:attribute>
          </xsl:element>
          <xsl:element name="text">
            <xsl:attribute name="x"><xsl:value-of select="(@from * $HSPACING) + $ACTIVITYBARWIDTH"/></xsl:attribute>
            <xsl:attribute name="y"><xsl:value-of select="(@t * $VSPACING) - 6"/></xsl:attribute>
            <xsl:attribute name="style">text-anchor: start;</xsl:attribute>
            <xsl:attribute name="filter">url(#textbg)</xsl:attribute>
            <xsl:choose>
              <xsl:when test="contains(messagetext/text(),'&#10;')">
                <xsl:value-of select="substring-before(messagetext/text(), '&#10;')"/>
                <xsl:call-template name="tspan">
                <xsl:with-param name="XPOS" select="(@from * $HSPACING) + (2 * $MESSAGEOFFSET)"/>
                  <xsl:with-param name="TEXT" select="substring-after(messagetext/text(), '&#10;')"/>
                </xsl:call-template>
              </xsl:when>
              <xsl:otherwise>
                <xsl:value-of select="messagetext/text()"/>
              </xsl:otherwise>
            </xsl:choose>
          </xsl:element>
        </xsl:when>
        <xsl:otherwise>
          <xsl:element name="line">
            <xsl:attribute name="x1"><xsl:value-of select="(@from * $HSPACING) + $MESSAGEOFFSET"/></xsl:attribute>
            <xsl:attribute name="y1"><xsl:value-of select="(@t * $VSPACING)"/></xsl:attribute>
            <xsl:attribute name="x2"><xsl:value-of select="(@to * $HSPACING) - $MESSAGEOFFSETTO"/></xsl:attribute>
            <xsl:attribute name="y2"><xsl:value-of select="@t * $VSPACING"/></xsl:attribute>
            <xsl:attribute name="style"><xsl:value-of select="$LINESTROKE"/></xsl:attribute>
            <xsl:attribute name="marker-end"><xsl:value-of select="$ARROWTYPE"/></xsl:attribute>
          </xsl:element>
          <xsl:element name="text">
            <xsl:attribute name="x"><xsl:value-of select="(@from * $HSPACING) + (2 * $MESSAGEOFFSET)"/></xsl:attribute>
            <xsl:attribute name="y"><xsl:value-of select="(@t * $VSPACING) - 6"/></xsl:attribute>
            <xsl:attribute name="style"><xsl:value-of select="$MESSAGEANCHOR"/></xsl:attribute>
            <xsl:attribute name="filter">url(#textbg)</xsl:attribute>
            <xsl:choose>
              <xsl:when test="contains(messagetext/text(),'&#10;')">
                <xsl:value-of select="substring-before(messagetext/text(), '&#10;')"/>
                <xsl:call-template name="tspan">
                <xsl:with-param name="XPOS" select="(@from * $HSPACING) + (2 * $MESSAGEOFFSET)"/>
                  <xsl:with-param name="TEXT" select="substring-after(messagetext/text(), '&#10;')"/>
                </xsl:call-template>
              </xsl:when>
              <xsl:otherwise>
                <xsl:value-of select="messagetext/text()"/>
              </xsl:otherwise>
            </xsl:choose>
          </xsl:element>
          <xsl:if test="$BOUNDINGRECTS = 'yes'">
            <xsl:element name="rect">
              <xsl:attribute name="x"><xsl:value-of select="$XBOUNDRECT"/></xsl:attribute>
              <xsl:attribute name="y"><xsl:value-of select="(@t * $VSPACING) - 3.5"/></xsl:attribute>
              <xsl:attribute name="width"><xsl:value-of select="$WIDTHBOUNDRECT"/></xsl:attribute>
              <xsl:attribute name="height">7</xsl:attribute>
              <xsl:attribute name="visibility">hidden</xsl:attribute>
            </xsl:element>
          </xsl:if>

          <xsl:if test="count(response)">
            <xsl:element name="line">
              <xsl:attribute name="x1"><xsl:value-of select="(@to * $HSPACING) - $MESSAGEOFFSET"/></xsl:attribute>
              <xsl:attribute name="y1"><xsl:value-of select="response/@t * $VSPACING"/></xsl:attribute>
              <xsl:attribute name="x2"><xsl:value-of select="(@from * $HSPACING) + $MESSAGEOFFSET"/></xsl:attribute>
              <xsl:attribute name="y2"><xsl:value-of select="response/@t * $VSPACING"/></xsl:attribute>
              <xsl:attribute name="style">stroke: black; stroke-width: 2; stroke-dasharray: 5 5;</xsl:attribute>
              <xsl:attribute name="marker-end"><xsl:value-of select="$ARROWTYPE"/></xsl:attribute>
            </xsl:element>
            <xsl:element name="text">
              <xsl:attribute name="x"><xsl:value-of select="(@to * $HSPACING) - (2 * $MESSAGEOFFSET)"/></xsl:attribute>
              <xsl:attribute name="y"><xsl:value-of select="(response/@t * $VSPACING) - 6"/></xsl:attribute>
              <xsl:attribute name="style"><xsl:value-of select="$RESPONSEANCHOR"/></xsl:attribute>
              <xsl:attribute name="filter">url(#textbg)</xsl:attribute>
              <xsl:choose>
                <xsl:when test="contains(response/text(),'&#10;')">
                  <xsl:value-of select="substring-before(response/text(), '&#10;')"/>
                  <xsl:call-template name="tspan">
                    <xsl:with-param name="XPOS" select="(@to * $HSPACING) - (2 * $MESSAGEOFFSET)"/>
                    <xsl:with-param name="TEXT" select="substring-after(response/text(), '&#10;')"/>
                  </xsl:call-template>
                </xsl:when>
                <xsl:otherwise>
                  <xsl:value-of select="response/text()"/>
                </xsl:otherwise>
              </xsl:choose>
            </xsl:element>
            <xsl:if test="$BOUNDINGRECTS = 'yes'">
              <xsl:element name="rect">
                <xsl:attribute name="x"><xsl:value-of select="$XBOUNDRECT"/></xsl:attribute>
                <xsl:attribute name="y"><xsl:value-of select="(response/@t * $VSPACING) - 3.5"/></xsl:attribute>
                <xsl:attribute name="width"><xsl:value-of select="$WIDTHBOUNDRECT"/></xsl:attribute>
                <xsl:attribute name="height">7</xsl:attribute>
                <xsl:attribute name="visibility">hidden</xsl:attribute>
              </xsl:element>
            </xsl:if>
          </xsl:if>
        </xsl:otherwise>
      </xsl:choose>
    </xsl:element>
  </xsl:template>

  <xsl:template match="frame">
    <xsl:variable name="FRAMEIDX" select="count(preceding-sibling::frame)"/>
    <xsl:element name="g">
      <xsl:attribute name="id"><xsl:value-of select="concat('frame_', $FRAMEIDX)"/></xsl:attribute>
      <xsl:attribute name="pointer-events">visiblePainted</xsl:attribute>
      <xsl:attribute name="style"><xsl:value-of select="$FONTSTRING"/></xsl:attribute>
      <xsl:choose>
        <xsl:when test="@type = 'SD'">
          <xsl:variable name="WIDTHFACTOR">
            <xsl:choose>
              <xsl:when test="count(@widthfactor)"><xsl:value-of select="@widthfactor"/></xsl:when>
              <xsl:otherwise>1</xsl:otherwise>
            </xsl:choose>
          </xsl:variable>
          <xsl:element name="rect">
            <xsl:attribute name="x"><xsl:value-of select="1 - ($HSPACING div 2)"/></xsl:attribute>
            <xsl:attribute name="y"><xsl:value-of select="$VOFFSET + 1"/></xsl:attribute>
            <xsl:attribute name="width"><xsl:value-of select="$SVGWIDTH - 2"/></xsl:attribute>
            <xsl:attribute name="height"><xsl:value-of select="$SVGHEIGHT - 2"/></xsl:attribute>
            <xsl:attribute name="style">stroke: black; fill: none; stroke-width: 2;</xsl:attribute>
          </xsl:element>
          <xsl:element name="polygon">
            <xsl:attribute name="points"><xsl:value-of select="concat(1 - ($HSPACING div 2), ',', $VOFFSET + 1, ' ', ($WIDTHFACTOR - 0.5) * $HSPACING, ',', $VOFFSET + 1, ' ', ($WIDTHFACTOR - 0.5) * $HSPACING, ',', $VOFFSET + 21, ' ', (($WIDTHFACTOR - 0.5) * $HSPACING) - 20, ',', $VOFFSET + 41,' ', 1 - ($HSPACING div 2), ',', $VOFFSET + 41)"/></xsl:attribute>
            <xsl:attribute name="style">stroke: black; fill: white; stroke-width: 2;</xsl:attribute>
          </xsl:element>
          <xsl:element name="text">
            <xsl:attribute name="x"><xsl:value-of select="10 - ($HSPACING div 2)"/></xsl:attribute>
            <xsl:attribute name="y"><xsl:value-of select="$VOFFSET + 21"/></xsl:attribute>
            <xsl:attribute name="style">text-anchor: start;</xsl:attribute>
            <xsl:attribute name="dominant-baseline">middle</xsl:attribute>
            <xsl:element name="tspan">
              <xsl:attribute name="style">font-weight: bold;</xsl:attribute>
              <xsl:value-of select="'SD '"/>
            </xsl:element>
            <xsl:value-of select="./text()"/>
          </xsl:element>
        </xsl:when>
        <xsl:otherwise>
          <xsl:variable name="FRAMEPADDING">
            <xsl:choose>
              <xsl:when test="@narrow = 'true'">0.15</xsl:when>
              <xsl:otherwise>0.25</xsl:otherwise>
            </xsl:choose>
          </xsl:variable>
          <xsl:element name="rect">
            <xsl:attribute name="x"><xsl:value-of select="$HSPACING  * (@left - $FRAMEPADDING)"/></xsl:attribute>
            <xsl:attribute name="y"><xsl:value-of select="$VSPACING * @top"/></xsl:attribute>
            <xsl:attribute name="width"><xsl:value-of select="$HSPACING * (@right - @left + (2 * $FRAMEPADDING))"/></xsl:attribute>
            <xsl:attribute name="height"><xsl:value-of select="$VSPACING * (@bottom - @top)"/></xsl:attribute>
            <xsl:attribute name="style">stroke: black; fill: none; stroke-width: 2;</xsl:attribute>
          </xsl:element>
          <xsl:element name="use">
            <xsl:attribute name="href">#frame-polygon</xsl:attribute>
            <xsl:attribute name="x"><xsl:value-of select="$HSPACING  * (@left - $FRAMEPADDING)"/></xsl:attribute>
            <xsl:attribute name="y"><xsl:value-of select="$VSPACING * @top"/></xsl:attribute>
          </xsl:element>
          <xsl:element name="text">
            <xsl:attribute name="x"><xsl:value-of select="($HSPACING  * (@left - $FRAMEPADDING)) + 10"/></xsl:attribute>
            <xsl:attribute name="y"><xsl:value-of select="($VSPACING * @top) + 5"/></xsl:attribute>
            <xsl:attribute name="style">text-anchor: start;font-weight: bold;</xsl:attribute>
            <xsl:attribute name="dominant-baseline">hanging</xsl:attribute>
            <xsl:value-of select="@type"/>
          </xsl:element>
          <xsl:element name="text">
            <xsl:attribute name="x"><xsl:value-of select="($HSPACING  * @left) + 30"/></xsl:attribute>
            <xsl:attribute name="y"><xsl:value-of select="($VSPACING * @top) + 15"/></xsl:attribute>
            <xsl:attribute name="style">text-anchor: start;</xsl:attribute>
            <xsl:attribute name="dominant-baseline">middle</xsl:attribute>
            <xsl:attribute name="filter">url(#textbg)</xsl:attribute>
            <xsl:value-of select="./text()"/>
          </xsl:element>
          <xsl:if test="@type = 'ALT'">
            <xsl:element name="line">
              <xsl:attribute name="x1"><xsl:value-of select="$HSPACING  * (@left - $FRAMEPADDING)"/></xsl:attribute>
              <xsl:attribute name="y1"><xsl:value-of select="@altt * $VSPACING"/></xsl:attribute>
              <xsl:attribute name="x2"><xsl:value-of select="$HSPACING * (@right + $FRAMEPADDING)"/></xsl:attribute>
              <xsl:attribute name="y2"><xsl:value-of select="@altt * $VSPACING"/></xsl:attribute>
              <xsl:attribute name="style">stroke: black; fill: none; stroke-width: 2; stroke-dasharray: 5 5;</xsl:attribute>
            </xsl:element>
            <xsl:element name="text">
              <xsl:attribute name="x"><xsl:value-of select="($HSPACING  * @left) + 30"/></xsl:attribute>
              <xsl:attribute name="y"><xsl:value-of select="($VSPACING * @altt) + 5"/></xsl:attribute>
              <xsl:attribute name="style">text-anchor: start;</xsl:attribute>
              <xsl:attribute name="dominant-baseline">hanging</xsl:attribute>
              <xsl:attribute name="filter">url(#textbg)</xsl:attribute>
              <xsl:value-of select="@alttext"/>
            </xsl:element>
          </xsl:if>
        </xsl:otherwise>
      </xsl:choose>
    </xsl:element>
  </xsl:template>

  <xsl:template name="tspan">
    <xsl:param name="XPOS"/>
    <xsl:param name="TEXT"/>
    <xsl:variable name="DY"><xsl:value-of select="$FONTSIZE * 2"/></xsl:variable>
    <xsl:element name="tspan">
      <xsl:attribute name="x"><xsl:value-of select="$XPOS"/></xsl:attribute>
      <xsl:attribute name="dy"><xsl:value-of select="$DY"/></xsl:attribute>
      <xsl:value-of select="concat( substring(substring-before($TEXT, '&#10;'), 1 div (contains($TEXT, '&#10;'))), substring($TEXT, 1 div not(contains($TEXT, '&#10;'))))"/>
    </xsl:element>
    <xsl:choose>
      <xsl:when test="contains($TEXT,'&#10;')">
        <xsl:call-template name="tspan">
          <xsl:with-param name="XPOS" select="$XPOS"/>
          <xsl:with-param name="TEXT" select="substring-after($TEXT, '&#10;')"/>
        </xsl:call-template>
      </xsl:when>
      <xsl:otherwise/>
    </xsl:choose>
  </xsl:template>

  <xsl:template name="tick">
    <xsl:param name="I" />
    <xsl:element name="line">
      <xsl:attribute name="x1"><xsl:value-of select="10 - ($HSPACING div 2)"/></xsl:attribute>
      <xsl:attribute name="y1"><xsl:value-of select="$I * $VSPACING"/></xsl:attribute>
      <xsl:attribute name="x2"><xsl:value-of select="20 - ($HSPACING div 2)"/></xsl:attribute>
      <xsl:attribute name="y2"><xsl:value-of select="$I * $VSPACING"/></xsl:attribute>
      <xsl:attribute name="style">stroke: grey; stroke-width: 2;</xsl:attribute>
    </xsl:element>
    <xsl:if test="not($I mod 5)">
      <xsl:element name="text">
        <xsl:attribute name="dominant-baseline">middle</xsl:attribute>
        <xsl:attribute name="x"><xsl:value-of select="25 - ($HSPACING div 2)"/></xsl:attribute>
        <xsl:attribute name="y"><xsl:value-of select="$I * $VSPACING"/></xsl:attribute>
        <xsl:attribute name="style">text-anchor: start;</xsl:attribute>
        <xsl:value-of select="$I"/>
      </xsl:element>
    </xsl:if>
    <!--begin_: RepeatTheLoopUntilFinished-->
    <xsl:if test="0 &lt; $I">
      <xsl:call-template name="tick">
        <xsl:with-param name="I"><xsl:value-of select="$I - 1"/></xsl:with-param>
      </xsl:call-template>
    </xsl:if>
  </xsl:template>

</xsl:stylesheet>
