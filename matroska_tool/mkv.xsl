<xsl:stylesheet version="2.0" xmlns:xsl="http://www.w3.org/1999/XSL/Transform" xmlns="urn:ietf:rfc:8794" xmlns:matroska="urn:ietf:rfc:8794">
<xsl:output method="text" omit-xml-declaration="yes" indent="no"/>

  <xsl:template match="/">
    <xsl:apply-templates select="/matroska:EBMLSchema/matroska:element"/>
  </xsl:template>

  <xsl:template match="matroska:element">
    <xsl:variable name="enum">
        <xsl:for-each select="matroska:restriction/matroska:enum">
            <xsl:choose>
                <xsl:when test="../../@type eq 'uinteger'">
                    <xsl:value-of select="concat(@value, ': ''', replace(@label, '''', '\\'''), '''')"/>
                </xsl:when>
                <xsl:otherwise>
                    <xsl:value-of select="concat('''', @value, ''': ''', replace(@label, '''', '\\'''), '''')"/>
                </xsl:otherwise>
            </xsl:choose>
            <xsl:if test="position() != last()">, </xsl:if>
        </xsl:for-each>
    </xsl:variable>
    <xsl:variable name="documentation">
        <xsl:for-each select="matroska:documentation">
            <xsl:value-of select="concat(@purpose, ':- ', replace(replace(., '&#10;', '\\n'), '''', ''''''), '\n')"/>
        </xsl:for-each>
    </xsl:variable>
    <xsl:value-of select="concat('  ', @id, ': {''name'': ''', @name, ''',', codepoints-to-string(10))"/>
    <xsl:value-of select="concat('    ''type'': ''', @type, ''',', codepoints-to-string(10))"/>
    <xsl:choose>
        <xsl:when test="@id eq '0xBF' or @id eq '0xEC'">
            <xsl:value-of select="concat('    ''level'': ', 7, ',', codepoints-to-string(10))"/>
        </xsl:when>
        <xsl:otherwise>
            <xsl:value-of select="concat('    ''level'': ', string-length(@path) - string-length(translate(@path, '\', '')) -1, ',', codepoints-to-string(10))"/>
        </xsl:otherwise>
    </xsl:choose>
    <xsl:if test="@default">
        <xsl:value-of select="concat('    ''default'': ''', @default, ''',', codepoints-to-string(10))"/>
    </xsl:if>
    <xsl:if test="string-length($enum) ne 0">
        <xsl:value-of select="concat('    ''enum'': {', $enum, '},', codepoints-to-string(10))"/>
    </xsl:if>
    <xsl:value-of select="concat('    ''documentation'': ''', $documentation, '''},', codepoints-to-string(10))"/>
  </xsl:template>

</xsl:stylesheet>
