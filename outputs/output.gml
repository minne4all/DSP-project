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
                    <imaer:name>Residential Area Development</imaer:name>
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
    <imaer:OffRoadMobileSourceEmissionSource sectorId="3210" gml:id="ES.1">
        <imaer:identifier>
            <imaer:NEN3610ID>
                <imaer:namespace>NL.IMAER</imaer:namespace>
                <imaer:localId>ES.1</imaer:localId>
            </imaer:NEN3610ID>
        </imaer:identifier>
        <imaer:label>Excavation site</imaer:label>
        <imaer:geometry>
            <imaer:EmissionSourceGeometry>
                <imaer:GM_Point>
                    <gml:Point srsName="urn:ogc:def:crs:EPSG::28992" gml:id="ES.1.POINT">
                        <gml:pos>138245.11583246976 474090.25857302056</gml:pos>
                    </gml:Point>
                </imaer:GM_Point>
            </imaer:EmissionSourceGeometry>
        </imaer:geometry>
        <imaer:emission>
            <imaer:Emission substance="NH3">
                <imaer:value>22.0</imaer:value>
            </imaer:Emission>
        </imaer:emission>
        <imaer:emission>
            <imaer:Emission substance="NOX">
                <imaer:value>55.0</imaer:value>
            </imaer:Emission>
        </imaer:emission>
        <imaer:emission>
            <imaer:Emission substance="PM10">
                <imaer:value>12.0</imaer:value>
            </imaer:Emission>
        </imaer:emission>
        <imaer:emission>
            <imaer:Emission substance="NO2">
                <imaer:value>17.0</imaer:value>
            </imaer:Emission>
        </imaer:emission>
        <imaer:offRoadMobileSource>
    <imaer:StandardOffRoadMobileSource offRoadMobileSourceType="B2T">
        <imaer:description>Excavator used for clearing land and digging foundations.</imaer:description>
        <imaer:literFuelPerYear>1400</imaer:literFuelPerYear>
    </imaer:StandardOffRoadMobileSource>
</imaer:offRoadMobileSource><imaer:offRoadMobileSource>
    <imaer:StandardOffRoadMobileSource offRoadMobileSourceType="LPG">
        <imaer:description>Mobile operator for moving stuff.</imaer:description>
        <imaer:literFuelPerYear>1200</imaer:literFuelPerYear>
    </imaer:StandardOffRoadMobileSource>
</imaer:offRoadMobileSource>
        </imaer:OffRoadMobileSourceEmissionSource>
</imaer:featureMember><imaer:featureMember>
    <imaer:OffRoadMobileSourceEmissionSource sectorId="3210" gml:id="ES.2">
        <imaer:identifier>
            <imaer:NEN3610ID>
                <imaer:namespace>NL.IMAER</imaer:namespace>
                <imaer:localId>ES.2</imaer:localId>
            </imaer:NEN3610ID>
        </imaer:identifier>
        <imaer:label>Bulldozer</imaer:label>
        <imaer:geometry>
            <imaer:EmissionSourceGeometry>
                <imaer:GM_Point>
                    <gml:Point srsName="urn:ogc:def:crs:EPSG::28992" gml:id="ES.2.POINT">
                        <gml:pos>138246.11674459855 474092.25958603785</gml:pos>
                    </gml:Point>
                </imaer:GM_Point>
            </imaer:EmissionSourceGeometry>
        </imaer:geometry>
        <imaer:emission>
            <imaer:Emission substance="NH3">
                <imaer:value>15.0</imaer:value>
            </imaer:Emission>
        </imaer:emission>
        <imaer:emission>
            <imaer:Emission substance="NOX">
                <imaer:value>48.0</imaer:value>
            </imaer:Emission>
        </imaer:emission>
        <imaer:emission>
            <imaer:Emission substance="PM10">
                <imaer:value>9.0</imaer:value>
            </imaer:Emission>
        </imaer:emission>
        <imaer:emission>
            <imaer:Emission substance="NO2">
                <imaer:value>13.0</imaer:value>
            </imaer:Emission>
        </imaer:emission>
        <imaer:offRoadMobileSource>
    <imaer:StandardOffRoadMobileSource offRoadMobileSourceType="LPG">
        <imaer:description>Mobile operator for moving stuff.</imaer:description>
        <imaer:literFuelPerYear>1200</imaer:literFuelPerYear>
    </imaer:StandardOffRoadMobileSource>
</imaer:offRoadMobileSource>
        </imaer:OffRoadMobileSourceEmissionSource>
</imaer:featureMember><imaer:featureMember>
    <imaer:OffRoadMobileSourceEmissionSource sectorId="3210" gml:id="ES.3">
        <imaer:identifier>
            <imaer:NEN3610ID>
                <imaer:namespace>NL.IMAER</imaer:namespace>
                <imaer:localId>ES.3</imaer:localId>
            </imaer:NEN3610ID>
        </imaer:identifier>
        <imaer:label>Cement Mixer</imaer:label>
        <imaer:geometry>
            <imaer:EmissionSourceGeometry>
                <imaer:GM_Point>
                    <gml:Point srsName="urn:ogc:def:crs:EPSG::28992" gml:id="ES.3.POINT">
                        <gml:pos>138247.11789031589 474094.26082949835</gml:pos>
                    </gml:Point>
                </imaer:GM_Point>
            </imaer:EmissionSourceGeometry>
        </imaer:geometry>
        <imaer:emission>
            <imaer:Emission substance="NH3">
                <imaer:value>8.0</imaer:value>
            </imaer:Emission>
        </imaer:emission>
        <imaer:emission>
            <imaer:Emission substance="NOX">
                <imaer:value>38.0</imaer:value>
            </imaer:Emission>
        </imaer:emission>
        <imaer:emission>
            <imaer:Emission substance="PM10">
                <imaer:value>7.0</imaer:value>
            </imaer:Emission>
        </imaer:emission>
        <imaer:emission>
            <imaer:Emission substance="NO2">
                <imaer:value>10.0</imaer:value>
            </imaer:Emission>
        </imaer:emission>
        <imaer:offRoadMobileSource>
    <imaer:StandardOffRoadMobileSource offRoadMobileSourceType="B4T">
        <imaer:description>Cement mixer used for transporting and mixing cement for construction.</imaer:description>
        <imaer:literFuelPerYear>1300</imaer:literFuelPerYear>
    </imaer:StandardOffRoadMobileSource>
</imaer:offRoadMobileSource>
        </imaer:OffRoadMobileSourceEmissionSource>
</imaer:featureMember><imaer:featureMember>
    <imaer:OffRoadMobileSourceEmissionSource sectorId="3210" gml:id="ES.4">
        <imaer:identifier>
            <imaer:NEN3610ID>
                <imaer:namespace>NL.IMAER</imaer:namespace>
                <imaer:localId>ES.4</imaer:localId>
            </imaer:NEN3610ID>
        </imaer:identifier>
        <imaer:label>Forklift</imaer:label>
        <imaer:geometry>
            <imaer:EmissionSourceGeometry>
                <imaer:GM_Point>
                    <gml:Point srsName="urn:ogc:def:crs:EPSG::28992" gml:id="ES.4.POINT">
                        <gml:pos>138248.11856734032 474096.26173290588</gml:pos>
                    </gml:Point>
                </imaer:GM_Point>
            </imaer:EmissionSourceGeometry>
        </imaer:geometry>
        <imaer:emission>
            <imaer:Emission substance="NH3">
                <imaer:value>5.0</imaer:value>
            </imaer:Emission>
        </imaer:emission>
        <imaer:emission>
            <imaer:Emission substance="NOX">
                <imaer:value>20.0</imaer:value>
            </imaer:Emission>
        </imaer:emission>
        <imaer:emission>
            <imaer:Emission substance="PM10">
                <imaer:value>6.0</imaer:value>
            </imaer:Emission>
        </imaer:emission>
        <imaer:emission>
            <imaer:Emission substance="NO2">
                <imaer:value>9.0</imaer:value>
            </imaer:Emission>
        </imaer:emission>
        <imaer:offRoadMobileSource>
    <imaer:StandardOffRoadMobileSource offRoadMobileSourceType="MUT">
        <imaer:description>Forklift used for moving materials around the construction site.</imaer:description>
        <imaer:operatingHoursPerYear>900</imaer:operatingHoursPerYear>
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