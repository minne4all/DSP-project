<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<imaer:FeatureCollectionCalculator xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
    xmlns:xlink="http://www.w3.org/1999/xlink" xmlns:imaer="http://imaer.aerius.nl/6.0"
    xmlns:gml="http://www.opengis.net/gml/3.2" gml:id="NL.IMAER.Collection"
    xsi:schemaLocation="http://imaer.aerius.nl/6.0 https://imaer.aerius.nl/6.0/IMAER.xsd">
    <imaer:metadata>
        <imaer:AeriusCalculatorMetadata>
            <imaer:project>
                <imaer:ProjectMetadata>
                    <imaer:year>2025</imaer:year>
                </imaer:ProjectMetadata>
            </imaer:project>
            <imaer:situation>
                <imaer:SituationMetadata>
                    <imaer:name>hello its me</imaer:name>
                    <imaer:reference>Rxa7Z4h3L1Cx</imaer:reference>
                    <imaer:situationType>PROPOSED</imaer:situationType>
                </imaer:SituationMetadata>
            </imaer:situation>
            <imaer:version>
                <imaer:VersionMetadata>
                    <imaer:aeriusVersion>2024.0.1_20241009_75e59949f9</imaer:aeriusVersion>
                    <imaer:databaseVersion>2024_75e59949f9_calculator_nl_stable</imaer:databaseVersion>
                </imaer:VersionMetadata>
            </imaer:version>
        </imaer:AeriusCalculatorMetadata>
    </imaer:metadata>
    <imaer:featureMember>
    <imaer:OffRoadMobileSourceEmissionSource sectorId="3220" gml:id="ES.1">
        <imaer:identifier>
            <imaer:NEN3610ID>
                <imaer:namespace>NL.IMAER</imaer:namespace>
                <imaer:localId>ES.1</imaer:localId>
            </imaer:NEN3610ID>
        </imaer:identifier>
        <imaer:label>sef</imaer:label>
        <imaer:geometry>
            <imaer:EmissionSourceGeometry>
                <imaer:GM_Point>
                    <gml:Point srsName="urn:ogc:def:crs:EPSG::28992" gml:id="ES.1.POINT">
                        <gml:pos>138238.12921947314 474076.28400205023</gml:pos>
                    </gml:Point>
                </imaer:GM_Point>
            </imaer:EmissionSourceGeometry>
        </imaer:geometry>
        <imaer:emission>
            <imaer:Emission substance="NH3">
                <imaer:value>128</imaer:value>
            </imaer:Emission>
        </imaer:emission>
        <imaer:emission>
            <imaer:Emission substance="NOX">
                <imaer:value>12309</imaer:value>
            </imaer:Emission>
        </imaer:emission>
        <imaer:emission>
            <imaer:Emission substance="PM10">
                <imaer:value>32198</imaer:value>
            </imaer:Emission>
        </imaer:emission>
        <imaer:emission>
            <imaer:Emission substance="NO2">
                <imaer:value>2828</imaer:value>
            </imaer:Emission>
        </imaer:emission>
        <imaer:offRoadMobileSource>
    <imaer:StandardOffRoadMobileSource offRoadMobileSourceType="MUT">
        <imaer:description>rnfk</imaer:description>
        <imaer:operatingHoursPerYear>123</imaer:operatingHoursPerYear>
    </imaer:StandardOffRoadMobileSource>
</imaer:offRoadMobileSource>
        </imaer:OffRoadMobileSourceEmissionSource>
</imaer:featureMember><imaer:featureMember>
    <imaer:CalculationPoint gml:id="CP.1">
        <imaer:identifier>
            <imaer:NEN3610ID>
                <imaer:namespace>NL.IMAER</imaer:namespace>
                <imaer:localId>CP.1</imaer:localId>
            </imaer:NEN3610ID>
        </imaer:identifier>
        <imaer:GM_Point>
            <gml:Point srsName="urn:ogc:def:crs:EPSG::28992" gml:id="CP.1.POINT">
                <gml:pos>136707.0 475063.0</gml:pos>
            </gml:Point>
        </imaer:GM_Point>
        <imaer:label>Oostelijke Vechtplassen (2 km)</imaer:label>
    </imaer:CalculationPoint>
</imaer:featureMember>
</imaer:FeatureCollectionCalculator>  