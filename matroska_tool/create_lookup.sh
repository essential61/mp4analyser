# bash script to generate Matroska tag lookup file from the Matroska specifications
MATROSKASPEC='https://raw.githubusercontent.com/ietf-wg-cellar/matroska-specification/refs/heads/master/ebml_matroska.xml'
EBMLSPEC='https://raw.githubusercontent.com/ietf-wg-cellar/ebml-specification/refs/heads/master/ebml.xml'
SAXON='saxon-he-12.9.jar'
XSLFILE="mkv.xsl"
LOOKUPOUT='idlookups.py'

curl -O $EBMLSPEC
curl -O $MATROSKASPEC

echo -e "\x27\x27\x27" > $LOOKUPOUT
echo -e "Python dictionary listing possible tags within a Matroska file\n" >> $LOOKUPOUT
echo -e "EBML specification from $EBMLSPEC \nMatroska specification from $MATROSKASPEC\n" >> $LOOKUPOUT
echo -e "An XSLT 2.0 transform $XSLFILE is applied to the EBML and Matroska specification files.\n" >> $LOOKUPOUT
echo -e "Output of transformations is merged and manipulated by $0 to produce $LOOKUPOUT" >> $LOOKUPOUT
echo -e "\x27\x27\x27\nid_table = {" >> $LOOKUPOUT

java -jar $SAXON  -s:ebml.xml -xsl:$XSLFILE >> $LOOKUPOUT
java -jar $SAXON  -s:ebml_matroska.xml -xsl:$XSLFILE >> $LOOKUPOUT
sed -i '$ s/,$//' $LOOKUPOUT

echo -e "}" >> $LOOKUPOUT
